This repository is a demo that use you only look once (yolov5) for real time object detection on raspberry Pi. 

To accelerate the inference process, a powerful GPU-based PC is used as the backend to run the yolov5 algorithm and then return the results back to raspberry Pi under a local area network (LAN). The communication structure of the PC and raspberry Pi is as follows:

![communication of gpu pc server and raspberry pi](https://github.com/weigao-123/Integration_Winter_2022_DU/blob/master/yolov5_raspberryPi_demo/img/communication%20of%20gpu%20pc%20server%20and%20raspberry%20pi.png)

##### **Environment Setup**:

- ***GPU PC*** (This is already provided by the instructors, so this part is covered, but if you would like to use your owner laptop as the backend of the inference engine as long as your laptop has a Nvidia GPU better than GTX 1050; In the meantime, a virtual python environment is also recommended, see instructions [here](#Appendix A)):

  - Retrieve the **gpu_pc_server** folder to your gpu pc server.

  - Once you have created a virtual python environment and activated it, you then install the following dependencies (under the **gpu_pc_server** folder):

    ```shell
    pip3 install -r requirements.txt
    ```

  - Then, to run the demo (under the **gpu_pc_server** folder). 

    ```shell
    python yolo_demo_server.py
    ```

    After you run this, if no error, then you should be able to see following information, which means that the server starts and is listening:

    ```python
    Socket created
    Socket bind complete
    Socket now listening
    ```

  - Since the gpu pc server and raspberry Pi communicate through TCP/IP protocol under LAN, you need to check the IP address of the gpu pc server and pass it to the raspberry pi client. On your server, check your IP address in command line:

    ```shell
    ipconfig
    ```

    Then you will see the related IP configuration, and the IPv4 Address is what needs to be used. An example is shown as follows:

    ```shell
    IPv4 Address. . . . . . . . . . . : 192.168.0.143
    ```

- ***Raspberry Pi***:

  - Retrieve the **raspberrypi_client** folder to you raspberry Pi.

  - Python >= 3.7 (only python=3.7 is tested, higher version should work; In the meantime, a virtual python environment is also recommended, see instructions [here](#Appendix B))

  - Once you have python environment ready, you then install the following dependencies (under the **raspberrypi_client** folder):

    ```shell
    pip3 install -r requirements.txt
    ```

  - Now, before we run the client script, make sure the gpu pc server IP address is obtained as above.

  - Then, to run the demo (under the **raspberrypi_client** folder) and pass the gpu pc server IP address (the IP address is just an example, you have to replace it to your own gpu server IP address):

    ```shell
    python3 yolo_demo_client.py 192.168.0.143
    ```

##### Appendix A

###### Set up virtual Python environment on Windows:

1. Python >= 3.7 (only python=3.7 is tested, higher version should work, but 3.7 is recommended) 

2. Install [Anaconda](https://www.anaconda.com/) (a convenient virtual python environment tool) first

3. Once Anaconda is installed and you can access it through the command line (the full documentation of Anaconda can be found [there](https://docs.anaconda.com/anaconda/user-guide/getting-started/)), some simple usage cases are as follows:

4. Create a new environment. yolov5_demo is the name of the environment which you can use of your choice; python=3.7 defines which version of Python interpreter you would like to use, here python 3.7 is used and recommended:

   ```shell
   conda create -n yolov5_demo python=3.7
   ```

5. To access the environment you just created. Once you can see **(yolov5_demo)** characters before your directory path in the command line, it means you are in the virtual environment now:

   ```shell
   conda activate yolov5_demo
   ```

###### Install pytorch on Windows

- Follow the instructions from the [Pytorch](https://pytorch.org/get-started/locally/) official website

##### Appendix B

###### Set up virtual Python environment on Raspberry Pi:

1. Python >= 3.7 (only python=3.7 is tested, higher version should work) 

2. Install [virtual]((a light virtual python environment tool) first

   ```shell
   sudo pip3 install virtualenv
   ```

3. Create a new environment. yolov5_demo is the name of the environment which you can use of your choice:

   ```shell
   virtualenv yolov5_demo
   ```

4. To access the environment you just created. Once you can see **(yolov5_demo)** characters before your directory path in the terminal, it means you are in the virtual environment now:

   ```shell
   source ./yolov5_demo/bin/activate
   ```

##### Appendix C

More information of Yolov5 can be found [here](https://github.com/ultralytics/yolov5).
