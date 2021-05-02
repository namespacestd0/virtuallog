# -*-coding:utf-8 -*-
## Loglet as the Server
import socket
import threading
import time
import json
import nodes

class SendDataThread(threading.Thread):
    def setDestination(self, clientSocket, recvDataThread):
        self.clientSocket = clientSocket
        self.recvDataThread = recvDataThread

    def terminate(self):
        self.running = False

    def run(self):
        self.running = True
        while (self.running):
            inputData = input("发给客户端:(request/over)")
            if inputData == "request":
                dataDict = {"color": "blue", "nid": 2, "payload": "server to client"}
                dataToSend = json.dumps(dataDict).encode("utf-8")
                self.clientSocket.send(dataToSend)
            elif inputData == "over":
                time.sleep(1)
                self.running = False
                self.clientSocket.close()
                self.recvDataThread.terminate()

class RecvDataThread(threading.Thread):
    def setSource(self, clientSocket, sendDataThread):
        self.clientSocket = clientSocket
        self.senDataThread = sendDataThread
        self.loglet = nodes.Loglet()

    def terminate(self):
        self.running = False

    def run(self):
        self.running = True
        while (self.running):
            try:
                dataReceived = self.clientSocket.recv(1024).decode("utf-8")
                if dataReceived != "":
                    print("\nHere is the dataReceived: ")
                    print(dataReceived)
                    dataDict = json.loads(dataReceived)

                    if dataDict["operation"] == "append":
                        print("Here is operation append.")
                        dictNode = dataDict["node"]
                        node = nodes.dictToNode(dictNode)
                        self.loglet.append(node)
                    elif dataDict["operation"] == "read_by_index":
                        print("Here is operation read_by_index.")
                        color = dataDict["color"]
                        index = dataDict["index"]
                        node = self.loglet.read_by_index(color, index)
                        if node == "Cannot find out the target node!":
                            dataToSend = node.encode("utf-8")
                        else:
                            dictNode = nodes.nodeToDict(node)
                            dataToSend = json.dumps(dictNode).encode("utf-8")
                        self.clientSocket.send(dataToSend)
                        print("send %s to client successfully.", dataToSend)
                    elif dataDict["operation"] == "read_by_target":
                        print("Here is operation read_by_target.")
                        targetNode = nodes.dictToNode(dataDict["target"])
                        node = self.loglet.read_by_target(dataDict["color"], targetNode)
                        if node == "Cannot find out the target node!":
                            dataToSend = node.encode("utf-8")
                        else:
                            dictNode = nodes.nodeToDict(node)
                            dataToSend = json.dumps(dictNode).encode("utf-8")
                        self.clientSocket.send(dataToSend)
                        print("send %s to client successfully.", dataToSend)
                    elif dataDict["operation"] == "over":
                        print("Here is operation over.")
                        self.running = False
                        self.clientSocket.close()
                        self.senDataThread.terminate()
                        print("The communication is over.")

                    
            except:
                pass

if __name__ == "__main__":
    tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServerSocket.bind(("", 2021))
    tcpServerSocket.listen(128)
 
    tcpClientSocket = None
    serverOnUse = False
 
    print("Waiting for client to connect...")
    tcpClientSocket, clientIp = tcpServerSocket.accept()
    print("New client is connected: %s" % str(clientIp))
 
    sendDataThread = SendDataThread()
    recvDataThread = RecvDataThread()
    sendDataThread.setDestination(tcpClientSocket, recvDataThread)
    recvDataThread.setSource(tcpClientSocket, sendDataThread)
 
    sendDataThread.start()
    recvDataThread.start()
 
    sendDataThread.join()
    recvDataThread.join()
 
    tcpServerSocket.close()