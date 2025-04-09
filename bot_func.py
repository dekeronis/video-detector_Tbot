from imageai.Detection import VideoObjectDetection

class RoadObjectDetector:
    def __init__(self, model_path="yolov3.pt", min_prob=30, fps=20):
        self.model_path = model_path
        self.min_prob = min_prob
        self.fps = fps
        self.detector = VideoObjectDetection()
        self.detections = []

        self._setup_detector()

    def _setup_detector(self):
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath(self.model_path)
        self.detector.loadModel()

    def _for_frame(self, frame_number, output_array, output_count):
        self.detections.extend(output_array)

    def detect_objects(self, video_path, output_path="detected_video"):
        self.detector.detectObjectsFromVideo(
            input_file_path=video_path,
            output_file_path=output_path,
            frames_per_second=self.fps,
            minimum_percentage_probability=self.min_prob,
            log_progress=True,
            per_frame_function=self._for_frame
        )
        return self.detections

    def filter_road_objects(self):
        target_objects = {"person", "bicycle", "car", "bus", "truck", "train"}
        return [obj for obj in self.detections if obj["name"] in target_objects]