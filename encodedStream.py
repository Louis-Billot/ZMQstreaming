import depthai as dai
import imagezmq
import zmq

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
ve1 = pipeline.create(dai.node.VideoEncoder)
ve2 = pipeline.create(dai.node.VideoEncoder)
ve3 = pipeline.create(dai.node.VideoEncoder)

ve1Out = pipeline.create(dai.node.XLinkOut)
ve2Out = pipeline.create(dai.node.XLinkOut)
ve3Out = pipeline.create(dai.node.XLinkOut)

ve1Out.setStreamName('ve1Out')
ve2Out.setStreamName('ve2Out')
ve3Out.setStreamName('ve3Out')

# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)

# Create encoders, one for each camera, consuming the frames and encoding them using H.264 / H.265 encoding
ve1.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_MAIN)
ve2.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H265_MAIN)
ve3.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_MAIN)

# Linking
monoLeft.out.link(ve1.input)
camRgb.video.link(ve2.input)
monoRight.out.link(ve3.input)
ve1.bitstream.link(ve1Out.input)
ve2.bitstream.link(ve2Out.input)
ve3.bitstream.link(ve3Out.input)

address = "tcp://192.168.137.1:5454"
# address = "tcp://localhost:5454"

context = imagezmq.SerializingContext()
socket = context.socket(zmq.PUB)
socket.connect(address)

# Connect to device and start pipeline
with dai.Device(pipeline) as dev:

    print('Connected cameras: ', dev.getConnectedCameras())
    print('Usb speed: ', dev.getUsbSpeed().name)

    # Output queues will be used to get the encoded data from the outputs defined above
    outQ1 = dev.getOutputQueue(name='ve1Out', maxSize=4, blocking=False)
    outQ2 = dev.getOutputQueue(name='ve2Out', maxSize=4, blocking=False)
    outQ3 = dev.getOutputQueue(name='ve3Out', maxSize=4, blocking=False)
    # outQ1 = dev.getOutputQueue(name='ve1Out', maxSize=30, blocking=True)
    # outQ2 = dev.getOutputQueue(name='ve2Out', maxSize=30, blocking=True)
    # outQ3 = dev.getOutputQueue(name='ve3Out', maxSize=30, blocking=True)

    while True:
        inLeft = outQ1.tryGet()
        inRgb = outQ2.tryGet()
        inRight = outQ3.tryGet()

        if inLeft is not None:
            socket.send_array(inLeft.getData(), msg="left", copy=False)

        if inRight is not None:
            socket.send_array(inRight.getData(), msg="right", copy=False)
        
        if inRgb is not None:
            socket.send_array(inRgb.getData(), msg="rgb", copy=False)

        # if cv2.waitKey(1) == ord('q'):
        #     break












    # The .h264 / .h265 files are raw stream files (not playable yet)
    with open('mono1.h264', 'wb') as fileMono1H264, open('color.h265', 'wb') as fileColorH265, open('mono2.h264', 'wb') as fileMono2H264:
        print("Press Ctrl+C to stop encoding...")
        while True:
            try:
                # Empty each queue
                while outQ1.has():
                    outQ1.get().getData().tofile(fileMono1H264)

                while outQ2.has():
                    outQ2.get().getData().tofile(fileColorH265)

                while outQ3.has():
                    outQ3.get().getData().tofile(fileMono2H264)
            except KeyboardInterrupt:
                # Keyboard interrupt (Ctrl + C) detected
                break

    print("To view the encoded data, convert the stream file (.h264/.h265) into a video file (.mp4), using commands below:")
    cmd = "ffmpeg -framerate 30 -i {} -c copy {}"
    print(cmd.format("mono1.h264", "mono1.mp4"))
    print(cmd.format("mono2.h264", "mono2.mp4"))
    print(cmd.format("color.h265", "color.mp4"))