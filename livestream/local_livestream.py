import cv2
import subprocess
import threading
from pytube import YouTube

class LocalLivestream:
    def __init__(self, stream_key='your_stream_key', output_url='rtmp://localhost/live'):
        self.stream_key = stream_key
        self.output_url = output_url
        self.current_url = None
        self.process = None
        self.capture = None
        self.is_streaming = False
        self.lock = threading.Lock()

    def get_stream_url(self, youtube_url):
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
        return stream.url

    def start_stream(self):
        self.is_streaming = True
        threading.Thread(target=self._capture_stream).start()

    def _capture_stream(self):
        while self.is_streaming:
            with self.lock:
                if self.current_url:
                    stream_url = self.get_stream_url(self.current_url)
                    self.capture = cv2.VideoCapture(stream_url)
                    if not self.capture.isOpened():
                        print(f"Error: Could not open video stream for URL {self.current_url}.")
                        self.is_streaming = False
                        return

                    command = [
                        'ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', f"{int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
                        '-r', str(self.capture.get(cv2.CAP_PROP_FPS)),
                        '-i', '-',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'veryfast',
                        '-f', 'flv',
                        f'{self.output_url}/{self.stream_key}'
                    ]

                    self.process = subprocess.Popen(command, stdin=subprocess.PIPE)

                    while self.is_streaming and self.capture.isOpened():
                        ret, frame = self.capture.read()
                        if not ret:
                            break
                        self.process.stdin.write(frame.tobytes())

                    self.capture.release()
                    self.process.stdin.close()
                    self.process.wait()

    def stop_stream(self):
        self.is_streaming = False
        if self.process:
            self.process.terminate()
        if self.capture and self.capture.isOpened():
            self.capture.release()

    def switch_stream(self, new_url):
        with self.lock:
            self.current_url = new_url
            if self.capture:
                self.capture.release()
            if self.process:
                self.process.terminate()
