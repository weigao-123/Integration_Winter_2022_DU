import socket
import cv2
import pickle
import struct
import time
import torch
from _thread import start_new_thread
import sys
import json


# Some Yolo parameters
CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]


def multi_threaded_client(conn, addr, models):
    while True:
        args = conn.recv(2048)
        if args:
            args = json.loads(args)
            model = models[args.get('model', 'general')]
            show_video = args.get('show_video', False)

            data = b""
            payload_size = struct.calcsize(">L")
            # print("payload_size: {}".format(payload_size))
            while True:
                while len(data) < payload_size:
                    # print("Recv: {}".format(len(dataset)))
                    tmp_data = conn.recv(4096)
                    if not tmp_data:
                        if show_video:
                            try:
                                cv2.destroyWindow("detections for {0}".format(addr))
                            except:
                                pass
                    else:
                        data += tmp_data
                # print("Done Recv: {}".format(len(dataset)))
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]
                # print("msg_size: {}".format(msg_size))
                while len(data) < msg_size:
                    tmp_data = conn.recv(4096)
                    if not tmp_data:
                        if show_video:
                            try:
                                cv2.destroyWindow("detections for {0}".format(addr))
                            except:
                                pass
                    else:
                        data += tmp_data
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


def start_yolo_server(models, port):
    # Port for comunication
    HOST = ''
    PORT = port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    s.bind((HOST, PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    process_count = 0
    thread_count = 0
    while True:
        conn, addr = s.accept()
        start_new_thread(multi_threaded_client, (conn, addr, models))
        thread_count += 1
        print('Thread Count on Port {0}: '.format(port), thread_count)
    s.close()


if __name__ == "__main__":
    # Load yolov5 model (The model can be pretrained general model or your own model)
    general_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')     # This model is from pytorch hub online

    # If you are going to use your own trained model, a example is shown as below
    flag_model = torch.hub.load('ultralytics/yolov5', 'custom', path=r'custom_trained_model.pt')

    models = {'general': general_model, 'flag_model': flag_model}
    port = int(sys.argv[1])
    start_yolo_server(models, port=port)
