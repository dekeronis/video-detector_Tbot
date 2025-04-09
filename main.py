from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram import F
from bot_func import RoadObjectDetector
import asyncio
import os

TOKEN = "7409424776:AAFPB8HDY7tUaVskUZ62k4Jq_M71FYMI30s"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_start(message: Message):
    await message.answer("Я умею анализировать видео с людьми и транспортом.\nСкинь любое видео.")

@dp.message(F.video | F.document)
async def handle_video(message: Message):
    file_info = message.video or message.document

    if not file_info.mime_type.startswith("video"):
        await message.answer("Пожалуйста, отправь именно видео.")
        return

    await message.answer("Скачиваю видео...")
    file = await bot.get_file(file_info.file_id)
    file_path = file.file_path
    file_id = file.file_unique_id
    input_path = f"downloads/{file_id}.mp4"
    output_path = f"downloads/{file_id}_detected"

    os.makedirs("downloads", exist_ok=True)
    await bot.download_file(file_path, destination=input_path)

    await message.answer("Анализирую видео, подожди...")

    detector = RoadObjectDetector(model_path="yolov3.pt")
    detector.detect_objects(input_path, output_path=output_path)
    filtered = detector.filter_road_objects()

    if not filtered:
        await message.answer("Ничего не найдено 😔")
    else:
        objects = [obj['name'] for obj in filtered]

        unique_objects = list(set(objects))
        summary = f"Найдены объекты: {', '.join(unique_objects)}"

        if len(summary) <= 4000:
            await message.answer(summary)
        else:
            list_path = f"downloads/{file_id}_objects.txt"
            with open(list_path, "w", encoding="utf-8") as f:
                f.write("\n".join(unique_objects))
            await message.answer_document(open(list_path, "rb"), caption="Список обнаруженных объектов")
            os.remove(list_path)


    detected_video_path = output_path + ".mp4"

    if os.path.exists(detected_video_path):
        video_file = FSInputFile(detected_video_path)
        await message.answer_video(video=video_file, caption="Вот обработанное видео 📹")

    os.remove(input_path)
    os.remove(detected_video_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
