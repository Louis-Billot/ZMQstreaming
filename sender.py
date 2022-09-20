import imagezmq
import zmq
import depthai as dai

import cv2

# Create pipeline
pipeline = dai.Pipeline()

# Define source and output
camRgb = pipeline.create(dai.node.ColorCamera)
xoutRgb = pipeline.create(dai.node.XLinkOut)
monoLeft = pipeline.create(dai.node.MonoCamera)
xoutLeft = pipeline.create(dai.node.XLinkOut)
monoRight = pipeline.create(dai.node.MonoCamera)
xoutRight = pipeline.create(dai.node.XLinkOut)
sysLog = pipeline.create(dai.node.SystemLogger)
xoutSysInfo = pipeline.create(dai.node.XLinkOut)
videoEncoder = pipeline.create(dai.node.VideoEncoder)
xoutJPG = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("rgb")
xoutLeft.setStreamName("left")
xoutRight.setStreamName("right")
xoutSysInfo.setStreamName("sysinfo")
xoutJPG.setStreamName("video")

# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_13_MP)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)

xoutLeft.input.setBlocking(False)
xoutLeft.input.setQueueSize(1)
xoutRight.input.setBlocking(False)
xoutRight.input.setQueueSize(1)

sysLog.setRate(2)
videoEncoder.setDefaultProfilePreset(camRgb.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)

# Linking
monoRight.out.link(xoutRight.input)
monoLeft.out.link(xoutLeft.input)
# camRgb.preview.link(xoutRgb.input)
sysLog.out.link(xoutSysInfo.input)
videoEncoder.bitstream.link(xoutJPG.input)
# camRgb.video.link(videoEncoder.input)

# address = "tcp://192.168.137.1:5454"
address = "tcp://localhost:5454"

context = imagezmq.SerializingContext()
socket = context.socket(zmq.PUB)
socket.connect(address)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    print('Connected cameras: ', device.getConnectedCameras())
    # Print out usb speed
    print('Usb speed: ', device.getUsbSpeed().name)

    # Output queues will be used to get the grayscale frames from the outputs defined above
    qLeft = device.getOutputQueue(name="left", maxSize=4, blocking=False)
    qRight = device.getOutputQueue(name="right", maxSize=4, blocking=False)

    while True:
        # Instead of get (blocking), we use tryGet (non-blocking) which will return the available data or None otherwise
        inLeft = qLeft.tryGet()
        inRight = qRight.tryGet()

        if inLeft is not None:
            # cv2.imshow("left", inLeft.getCvFrame())
            socket.send_array(inLeft.getCvFrame(), msg="left", copy=False)

        if inRight is not None:
            # cv2.imshow("right", inRight.getCvFrame())
            socket.send_array(inRight.getCvFrame(), msg="right", copy=False)

        # if cv2.waitKey(1) == ord('q'):
        #     break