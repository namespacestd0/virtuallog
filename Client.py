# -*- coding: utf-8 -*-
import socket
import json
import time
import nodes

address = ('172.22.157.18', 2021)
#address = ("192.168.0.1", 2021)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.connect(address)

#append
print("发给服务器：")
node = nodes.Node(nid = None, payload = "N/A", targets = ["RED", "YELLOW", "GREEN"])
request = {"operation": "append", "node": nodes.nodeToDict(node)}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print("The request from client is: ", dataToSend)
time.sleep(1)

node = nodes.Node(nid = 1, payload = "N/A", targets = ["RED", "YELLOW"])
request = {"operation": "append", "node": nodes.nodeToDict(node)}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print("The request from client is: ", dataToSend)
time.sleep(1)

node = nodes.Node(nid = 2, payload = "N/A", targets = ["GREEN"])
request = {"operation": "append", "node": nodes.nodeToDict(node)}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print("The request from client is: ", dataToSend)
time.sleep(1)

#read_by_index
request = {"operation": "read_by_index", "color": "RED", "index": 1}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print("The request from client is: ", dataToSend)

dataReceived = s.recv(1024).decode("utf-8")
if dataReceived == "Cannot find out the target node!":
    print(dataReceived)
else:
    dataDict = json.loads(dataReceived)
    print(dataDict)
    receivedNode = nodes.dictToNode(dataDict)
    print(receivedNode)
time.sleep(1)

#append
node = nodes.Node(nid = 3, payload = "N/A", targets = ["GREEN"])
request = {"operation": "append", "node": nodes.nodeToDict(node)}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print(dataToSend)
time.sleep(1)

#read_by_target
targetNode = nodes.Node(nid = 3)
request = {"operation": "read_by_target", "color": "GREEN", "target": nodes.nodeToDict(targetNode)}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print("The request from client is: ", dataToSend)

dataReceived = s.recv(1024).decode("utf-8")
if dataReceived == "Cannot find out the target node!":
    print(dataReceived)
else:
    dataDict = json.loads(dataReceived)
    print(dataDict)
    receivedNode = nodes.dictToNode(dataDict)
    print(receivedNode)
time.sleep(1)

#read_by_index --> don't find out
request = {"operation": "read_by_index", "color": "RED", "index": 5}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print("The request from client is: ", dataToSend)

dataReceived = s.recv(1024).decode("utf-8")
print(dataReceived)
if dataReceived != "Cannot find out the target node!":
    dataDict = json.loads(dataReceived)
    receivedNode = nodes.dictToNode(dataDict)
    print("The read result is: ", receivedNode)
time.sleep(1)

#read_by_target --> don't find out
targetNode = nodes.Node(nid = 8)
request = {"operation": "read_by_target", "color": "GREEN", "target": nodes.nodeToDict(targetNode)}
dataToSend = json.dumps(request).encode("utf-8")
s.send(dataToSend)
print("The request from client is: ", dataToSend)

dataReceived = s.recv(1024).decode("utf-8")
print(dataReceived)
if dataReceived != "Cannot find out the target node!":
    dataDict = json.loads(dataReceived)
    receivedNode = nodes.dictToNode(dataDict)
    print("The read result is: ", receivedNode)
time.sleep(1)

s.close()