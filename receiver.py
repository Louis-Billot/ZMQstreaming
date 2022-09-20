import imagezmq
import zmq
import cv2

import numpy as np

address = "tcp://*:5454"

context = imagezmq.SerializingContext()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b'')
socket.bind(address)


key = -1

while key != ord('q'):

    try:
        message, image = socket.recv_array(flags=zmq.Flag.DONTWAIT, copy=False)
    except zmq.error.Again:
            pass
    except Exception as e:
        print(message, e)
    else:
        cv2.imshow(message, image)

    key = cv2.waitKey(1)