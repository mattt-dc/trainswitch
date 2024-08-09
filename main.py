import time
import threading
from livestream.local_livestream import LocalLivestream
from livestream.stream_manager import StreamManager

def main():
    livestream = LocalLivestream()

    # Create and start the stream manager
    manager = StreamManager(livestream)
    manager.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        livestream.stop_stream()
        print("Streaming stopped.")

if __name__ == "__main__":
    main()
