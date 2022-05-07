import socket
import cv2
import pickle
import struct
import time
import torch
from _thread import start_new_thread


# Some Yolo parameters
CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]


def multi_threaded_client(conn, addr, model, show_video=True):
    data = b""
    payload_size = struct.calcsize(">L")
    # print("payload_size: {}".format(payload_size))
    while True:
        while len(data) < payload_size:
            # print("Recv: {}".format(len(dataset)))
            data += conn.recv(4096)

        # print("Done Recv: {}".format(len(dataset)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        # print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Receive video stream from raspberry Pi
        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        # Inference real time video using yolov5
        start = time.time()
        result = model(frame)
        end = time.time()

        if show_video:
            start_drawing = time.time()
            # Render the result in the video stream
            result.render()
            end_drawing = time.time()

            # Calculate the FPS
            fps_label = "FPS: %.2f" % (1 / (end - start))
            cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.imshow("detections for {0}".format(addr), frame)
            cv2.waitKey(1)

        # Inference results back to raspberry Pi
        back_data = result.pandas().xyxy[0].to_json()
        conn.sendall(bytes(back_data, encoding='utf-8'))
    conn.close()

def start_yolo_server(model):
    # Port for comunication
    HOST = ''
    PORT = 8000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    s.bind((HOST, PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    ThreadCount = 0
    while True:
        conn, addr = s.accept()
        start_new_thread(multi_threaded_client, (conn, addr, model,))
        ThreadCount += 1
        print('Thread Count: ', ThreadCount)
    s.close()


if __name__ == "__main__":
    # Load yolov5 model (The model can be pretrained general model or your own model)
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')     # This model is from pytorch hub online

    # If you are going to use your own trained model, a example is shown as below
    #model = torch.hub.load('ultralytics/yolov5', 'custom', path=r'custom_trained_model.pt')

    start_yolo_server(model)
