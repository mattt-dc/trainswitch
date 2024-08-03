import time
import threading
from livestream.local_livestream import LocalLivestream

class StreamManager:
    def __init__(self, livestream):
        self.livestream = livestream

    def stream_decision_thread(self):
        print("Starting stream decision thread...")
        # List of local video file paths
        video_paths = [
            'rtmp://localhost/live',
            'rtmp://localhost:1985/live2',
            # Add more paths as needed
        ]

        for path in video_paths:
            print(f"Switching to {path}...")
            self.livestream.switch_stream(path)
            print(f"Switched to {path}")
            time.sleep(60)

    def start(self):
        threading.Thread(target=self.stream_decision_thread).start()
