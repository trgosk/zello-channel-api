import sys
import time
from datetime import datetime

import zmq

port = "5557"
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(f"tcp://*:{port}")

topic = "VOX"

now = datetime.now()
messagedata = f"hello1 {now.strftime('%Y-%m-%d %H:%M:%S')}"
print(f"{topic} {messagedata}")
socket.send_string(f"{topic} {messagedata}")
###########################################################
time.sleep(0.2)
###########################################################
now = datetime.now()
messagedata = f"hello2 {now.strftime('%Y-%m-%d %H:%M:%S')}"
print(f"{topic} {messagedata}")
socket.send_string(f"{topic} {messagedata}")
###########################################################
time.sleep(0.2)
###########################################################
now = datetime.now()
messagedata = f"start {now.strftime('%Y-%m-%d %H:%M:%S')} 1"
print(f"{topic} {messagedata}")
socket.send_string(f"{topic} {messagedata}")
###########################################################
time.sleep(10)
###########################################################
now = datetime.now()
messagedata = f"stop {now.strftime('%Y-%m-%d %H:%M:%S')} 1"
print(f"{topic} {messagedata}")
socket.send_string(f"{topic} {messagedata}")
###########################################################
time.sleep(5)
###########################################################
now = datetime.now()
messagedata = f"start {now.strftime('%Y-%m-%d %H:%M:%S')} 2"
print(f"{topic} {messagedata}")
socket.send_string(f"{topic} {messagedata}")
###########################################################
time.sleep(10)
###########################################################
now = datetime.now()
messagedata = f"stop {now.strftime('%Y-%m-%d %H:%M:%S')} 2"
print(f"{topic} {messagedata}")
socket.send_string(f"{topic} {messagedata}")
###########################################################
time.sleep(2)
###########################################################
now = datetime.now()
messagedata = f"bye {now.strftime('%Y-%m-%d %H:%M:%S')}"
print(f"{topic} {messagedata}")
socket.send_string(f"{topic} {messagedata}")
