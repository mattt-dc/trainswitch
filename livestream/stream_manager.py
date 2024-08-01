import time
from livestream.local_livestream import LocalLivestream

class StreamManager:
    def __init__(self, livestream):
        self.livestream = livestream

    def stream_decision_thread(self):
        # List of local video file paths
        video_paths = [
            'rtmp://localhost/live',
            'rtmp://localhost/live2',
            # Add more paths as needed
        ]

        for path in video_paths:
            self.livestream.switch_stream(path)
            print(f"Switched to {path}")
            time.sleep(10)  # Stream each video for 10 seconds

    def start(self):
        threading.Thread(target=self.stream_decision_thread).start()
