# -*-coding:utf-8 -*-
import socket
import threading
import time

class SendDataThread(threading.Thread):
    def setDestination(self, clientSocket, recvDataThread):
        self.clientSocket = clientSocket
        self.recvDataThread = recvDataThread

    def terminate(self):
        self.running = False

    def run(self):
        self.running = True
        while (self.running):
            dataToSend = input("发给客户端：")
            if dataToSend != "\n" and dataToSend != "":
                self.clientSocket.send((dataToSend).encode("utf-8"))
            if dataToSend == "over":
                time.sleep(1)
                self.running = False
                self.clientSocket.close()
                self.recvDataThread.terminate()

class RecvDataThread(threading.Thread):
    def setSource(self, clientSocket, sendDataThread):
        self.clientSocket = clientSocket
        self.senDataThread = sendDataThread

    def terminate(self):
        self.running = False

    def run(self):
        self.running = True
        while (self.running):
            try:
                dataReceived = str(self.clientSocket.recv(1024), "utf-8")
                if dataReceived != "":
                    print("\n客户端来信：%s" % str(dataReceived))
                    if dataReceived == "over":
                        self.running = False
                        self.clientSocket.close()
                        self.senDataThread.terminate()
                        print("通信结束，按任意键关闭")
            except:
                pass

def main():
    tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServerSocket.bind(("", 2021))
    tcpServerSocket.listen(128)

    tcpClientSocket = None
    serverOnUse = False

    print("等待客户端连接")
    tcpClientSocket, clientIp = tcpServerSocket.accept()
    print("新的客户端已连接：%s" % str(clientIp))

    sendDataThread = SendDataThread()
    recvDataThread = RecvDataThread()
    sendDataThread.setDestination(tcpClientSocket, recvDataThread)