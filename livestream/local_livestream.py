import cv2
import subprocess
import threading
import time

class LocalLivestream:
    def __init__(self, stream_key='test', output_url='rtmp://localhost:1936'):
        self.stream_key = stream_key
        self.output_url = output_url
        self.current_path = None
        self.previous_path = None
        self.process = None
        self.capture = None
        self.is_streaming = False
        self.lock = threading.Lock()

    def start_stream(self):
        self.is_streaming = True
        print(f"Current active threads bf: {len(threading.enumerate())}")
        threading.Thread(target=self._capture_stream).start()
        print(f"Current active threads af: {len(threading.enumerate())}")

    def _capture_stream(self):
        self.initialize_ffmpeg_process()
        error_count = 0

        while self.is_streaming:
            with self.lock:
                if self.current_path:
                    self.switch_video_source(self.current_path)

                    while self.is_streaming and self.capture.isOpened():
                        if error_count > 10:
                            print("Too many errors. Restarting stream...")
                            self.stop_stream()
                            self.start_stream()
                            break
                        if self.current_path_has_changed():
                            self.switch_video_source(self.current_path)
                            continue

                        ret, frame = self.capture.read()
                        if not ret:
                            break
                        try:
                            self.process.stdin.write(frame.tobytes())
                        except Exception as e:
                            print(f"Error writing frame to ffmpeg process: {e}")
                            time.sleep(1)
                            error_count += 1
                            # break
                        error_count = 0

    def initialize_ffmpeg_process(self):
        command = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "1280x720",
            '-r', "30",
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'veryfast',
            '-f', 'flv',
            f'{self.output_url}/{self.stream_key}'
        ]
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE)

    def switch_video_source(self, new_path):
        if self.current_path == new_path and self.capture is not None:
            print(f"Video source is already {new_path}")
            time.sleep(10)
            return
        print(f"Switching video source to {new_path}...")
        self.previous_path = self.current_path
        if self.capture:
            self.capture.release()
        self.capture = cv2.VideoCapture(new_path)
        self.current_path = new_path

    def current_path_has_changed(self):
        return self.current_path != self.previous_path

    def stop_stream(self):
        self.is_streaming = False
        if self.process:
            self.process.terminate()
        if self.capture and self.capture.isOpened():
            self.capture.release()

    def switch_stream(self, new_path):
        print(f"Switching stream to {new_path}...")
        self.current_path = new_path
        with self.lock:
            print("Setting current path...")
            self.current_path = new_path
            if self.capture:
                self.capture.release()
            if self.process:
                self.process.terminate()
