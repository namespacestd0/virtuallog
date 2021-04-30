# -*- coding: utf-8 -*-
import socket
import json
import time

address = ('172.22.157.18', 2021)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.connect(address)

#send
print("发给服务器：")
node = {"color": "red'", "nid": 1, "payload": "N/A"}
dataToSend = json.dumps(node).encode("utf-8")
s.send(dataToSend)
print(dataToSend)
print(type(dataToSend))

#receive
data = s.recv(1024)
print(data)

s.close()