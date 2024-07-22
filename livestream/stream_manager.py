import time
from livestream.local_livestream import LocalLivestream

class StreamManager:
    def __init__(self, livestream):
        self.livestream = livestream

    def stream_decision_thread(self):
        # This is a placeholder for the logic that decides which stream to use
        youtube_urls = [
            'YOUR_FIRST_YOUTUBE_LIVESTREAM_URL',
            'YOUR_SECOND_YOUTUBE_LIVESTREAM_URL',
            # Add more URLs as needed
        ]

        for url in youtube_urls:
            self.livestream.switch_stream(url)
            print(f"Switched to {url}")
            time.sleep(10)  # Stream each URL for 10 seconds

    def start(self):
        threading.Thread(target=self.stream_decision_thread).start()
