@echo off
cd %~dp0
conda activate yolov5_demo
start /B python yolo_demo_server.py 8000
start /B python yolo_demo_server.py 8001
start /B python yolo_demo_server.py 8002
start /B python yolo_demo_server.py 8003
start /B python yolo_demo_server.py 8004
