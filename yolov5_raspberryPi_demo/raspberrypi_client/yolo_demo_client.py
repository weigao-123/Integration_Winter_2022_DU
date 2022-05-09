import cv2
import io
import socket
import struct
import time
import pickle
import zlib
import pandas as pd
import sys
import json


def yolo_tcp_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect server by provided server ip and server port
    client_socket.connect((server_ip, server_port))
    connection = client_socket.makefile('wb')

    # Start camera using opencv
    cam = cv2.VideoCapture(0)

    # Set the video picture side
    cam.set(3, 640)
    cam.set(4, 480)

    img_counter = 0

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    while True:
        ret, frame = cam.read()
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        # data = zlib.compress(pickle.dumps(frame, 0))
        data = pickle.dumps(frame, 0)
        size = len(data)

        # print("{}: {}".format(img_counter, size))
        start = time.time()
        client_socket.sendall(struct.pack(">L", size) + data)
        # client_socket.sendall(bytes('send', encoding='utf-8'))
        img_counter += 1

        # Get inference results from the gpu server
        recv_data = client_socket.recv(1024).decode('utf-8')
        recv_data = pd.read_json(recv_data)
        print('Time delay: {0} ms'.format((time.time() - start) * 1000))
        print(recv_data)

    cam.release()


def connect(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect server by provided server ip and server port
    client_socket.connect((server_ip, server_port))
    connection = client_socket.makefile('wb')
    return client_socket


def camera_initialization():
    # Start camera using opencv
    cam = cv2.VideoCapture(0)

    # Set the video picture side
    cam.set(3, 640)
    cam.set(4, 480)

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    return cam, encode_param


def get_inference_result(client_socket, frame, encode_param):
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    # data = zlib.compress(pickle.dumps(frame, 0))
    data = pickle.dumps(frame, 0)
    size = len(data)

    # print("{}: {}".format(img_counter, size))
    start = time.time()
    client_socket.sendall(struct.pack(">L", size) + data)
    # client_socket.sendall(bytes('send', encoding='utf-8'))

    # Get inference results from the gpu server
    recv_data = client_socket.recv(1024).decode('utf-8')
    try:
        recv_data = pd.read_json(recv_data)
        print('Time delay: {0} ms'.format((time.time() - start) * 1000))
        print(recv_data)
    except:
        pass

    
if __name__ == "__main__":
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client_socket = connect(server_ip, server_port)

    cam, encode_param = camera_initialization()

    # Specify arguments to the server for initialization
    args = {'model': 'general', 'show_video': True}
    client_socket.sendall(str.encode(json.dumps(args)))

    # Test 1
    for i in range(200):
        ret, frame = cam.read()
        get_inference_result(client_socket, frame, encode_param)
    print('~~~~~~~')
    time.sleep(3)
    for i in range(200):
        ret, frame = cam.read()
        get_inference_result(client_socket, frame, encode_param)
    print('~~~~~~~')

    ## Test 2
    # while True:
    #     ret, frame = cam.read()
    #     get_inference_result(client_socket, frame, encode_param)
    # ret, frame = cam.read()
    # get_inference_result(client_socket, frame, encode_param)
    # print('1st')
    # time.sleep(3)
    # ret, frame = cam.read()
    # get_inference_result(client_socket, frame, encode_param)
    # print('2st')

    ## Test 3
    # yolo_tcp_client(server_ip, server_port)
