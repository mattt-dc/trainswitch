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
        self.model.save = True

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
            self.livestream.switch_stream(video_paths[0])
            print("Switched stream")
            time.sleep(150)

        # self.livestream.switch_stream(video_paths[1])

        while True:
            for path in video_paths:
                cap = cv2.VideoCapture(path)
                success, frame = cap.read()
                if success:
                    # Save frame to a temporary file
                    temp_image_path = "temp_frame.jpg"
                    cv2.imwrite(temp_image_path, frame)
                    
                    # Predict using the saved image
                    print("Predicting...")
                    pred = self.model.predict(image=temp_image_path, img_size=640)
                    # Assuming 'pred' contains information to decide if a train is detected
                    # You might need to adjust the condition based on your prediction result structure
                    if "train" in pred:
                        print(f"Train detected in {path}. Switching...")
                        self.livestream.switch_stream(path)
                        time.sleep(10)
                        # Break the loop to switch to the detected stream
                        break
                else:
                    print(f"Failed to read from {path}")
                cap.release()
                time.sleep(1)  # Sleep to ensure we're checking approximately one frame per second

    def start(self):
        threading.Thread(target=self.stream_decision_thread).start()