import time
import threading
import cv2
from livestream.local_livestream import LocalLivestream
from yoloxdetect import YoloxDetector

class StreamManager:
    def __init__(self, livestream):
        self.livestream = livestream
        self.model = YoloxDetector(
            model_path = "data/weights/yolox_m.pth",
            config_path = "configs.yolox_m",
            device = "cpu",
            hf_model=False,
        )
        self.model.classes = None
        self.model.conf = 0.25
        self.model.iou = 0.45
        self.model.show = False
        self.model.save = False
        self.model.torchyolo = True

    def switch_stream_in_thread(self, path):
        threading.Thread(target=self.livestream.start_stream, args=(path,)).start()

    def stream_decision_thread(self):
        print("Starting stream decision thread...")
        # List of local video file paths
        video_paths = [
            'rtmp://localhost/live',
            'rtmp://localhost:1985/live2',
            # Add more paths as needed
        ]
        if self.livestream.current_path == None:
            print("Switching to the first stream in the list...")
            time.sleep(5)
            print(f"Current active threads: {len(threading.enumerate())}")
            self.switch_stream_in_thread(video_paths[0])
            print("Switched stream")
            time.sleep(5)

        # self.livestream.switch_stream(video_paths[1])

        while True:
            if not self.livestream.is_ready:
                time.sleep(1)
                continue
            for path in video_paths:
                if path == self.livestream.current_path:
                    continue
                cap = cv2.VideoCapture(path)
                success, frame = cap.read()
                if success:
                    temp_image_path = "data/images/temp_frame.jpg"
                    cv2.imwrite(temp_image_path, frame)
                    
                    try:
                        print("Predicting...")
                        pred = self.model.predict("data/images/temp_frame.jpg", 640)
                        predValue = pred[2][0].item()
                        if predValue == 6.0:
                            print(f"Train detected in {path}. Switching...")
                            # self.livestream.switch_stream(path)
                            self.livestream.switch_video_source(path)
                            time.sleep(30)
                            break
                    except Exception as e:
                        print(f"Error predicting: {e}")
                else:
                    print(f"Failed to read from {path}")
                cap.release()
                time.sleep(1)  # Sleep to ensure we're checking approximately one frame per second

    def start(self):
        threading.Thread(target=self.stream_decision_thread).start()