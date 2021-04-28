# -*- coding: utf-8 -*-
import socket

address = ('172.22.157.18', 2021)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.connect(address)

#send
dataToSend = input("发给服务器：")
s.send(dataToSend.encode("utf-8"))

#receive
data = s.recv(1024)
print(data)
s.close()