import cv2
import io
import socket
import struct
import time
import pickle
import zlib
import pandas as pd
import sys


def yolo_tcp_client(server_ip, server_port=8000):
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

        #print("{}: {}".format(img_counter, size))
        start = time.time()
        client_socket.sendall(struct.pack(">L", size) + data)
        #client_socket.sendall(bytes('send', encoding='utf-8'))
        img_counter += 1
        
        # Get inference results from the gpu server
        recv_data = client_socket.recv(1024).decode('utf-8')
        recv_data = pd.read_json(recv_data)
        print('Time delay: {0} ms'.format((time.time()-start) * 1000))
        print(recv_data)

    cam.release()


# UDP protocol is not working right now!
def yolo_udp_client():
    HOST = '192.168.0.182'
    PORT = 8000
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.connect((HOST, PORT))
    print('now starting to send frames...')
    capture = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = capture.read()
            while not success and frame is None:
                success, frame = capture.read()
            result, imgencode = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            start = time.time()
            server.sendall(struct.pack('i', imgencode.shape[0]))
            server.sendall(imgencode)
            recv_data, addr = server.recvfrom(1024)
            print('Time delay: {0} ms '.format((time.time() - start) * 1000))
            # print('have sent one frame')
    except Exception as e:
        print(e)
        server.sendall(struct.pack('c', 1))
        capture.release()
        server.close()


if __name__ == "__main__":
    server_ip = sys.argv[1]
    yolo_tcp_client(server_ip)
