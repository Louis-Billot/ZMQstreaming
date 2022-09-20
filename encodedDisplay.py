import subprocess
from datetime import datetime
import zmq
import imagezmq
import cv2

address = "tcp://*:5454"

context = imagezmq.SerializingContext()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b'')
socket.bind(address)

now = datetime.now()

key = -1

    # The .h264 / .h265 files are raw stream files (not playable yet)
with open('{}_mono1.h264'.format(now.strftime("%y-%m-%d_%H-%M-%S")), 'wb') as fileMono1H264, open('{}_color.h265'.format(now.strftime("%y-%m-%d_%H-%M-%S")), 'wb') as fileColorH265, open('{}_mono2.h264'.format(now.strftime("%y-%m-%d_%H-%M-%S")), 'wb') as fileMono2H264:
    print("Press Ctrl+C to stop encoding...")
    while key != ord('q'):
        try:
            message, image = socket.recv_array(flags=zmq.Flag.DONTWAIT, copy=False)
            # Empty each queue
        except zmq.error.Again:
            pass
        except KeyboardInterrupt:
            # Keyboard interrupt (Ctrl + C) detected
            break
        else:
            if message == "rgb":
                image.tofile(fileColorH265)
            elif message == "left":
                image.tofile(fileMono1H264)
            elif message == "right":
                image.tofile(fileMono2H264)
        # key = cv2.waitKey(1)

fileColorH265.close()
fileMono1H264.close()
fileMono2H264.close()

print("To view the encoded data, convert the stream file (.h264/.h265) into a video file (.mp4), using commands below:")
cmd = "ffmpeg -framerate 30 -i {} -c copy {}"
print(cmd.format("{}_mono1.h264".format(now.strftime("%y-%m-%d_%H-%M-%S")), "{}_mono1.mp4".format(now.strftime("%y-%m-%d_%H-%M-%S"))))
print(cmd.format("{}_mono2.h264".format(now.strftime("%y-%m-%d_%H-%M-%S")), "{}_mono2.mp4".format(now.strftime("%y-%m-%d_%H-%M-%S"))))
print(cmd.format("{}_color.h265".format(now.strftime("%y-%m-%d_%H-%M-%S")), "{}_color.mp4".format(now.strftime("%y-%m-%d_%H-%M-%S"))))

# print(os.system(cmd))

subprocess.call(cmd.format("{}_mono1.h264".format(now.strftime("%y-%m-%d_%H-%M-%S")), "{}_mono1.mp4".format(now.strftime("%y-%m-%d_%H-%M-%S"))), shell=True)
# subprocess.call("", shell=True)