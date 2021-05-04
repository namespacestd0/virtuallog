# -*-coding:utf-8 -*-
# Loglet as the Server
from json.decoder import JSONDecodeError
import socketserver
import json
import nodes

loglet = nodes.Loglet()

# TODO ERROR SERIALIZATION


class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls

        # telnet clear screen
        self.wfile.write("\u001B[2J".encode())

        while True:
            dataReceived = self.rfile.readline().strip()
            print("{} wrote:".format(self.client_address[0]))
            print(dataReceived)

            if dataReceived:
                try:
                    dataDict = json.loads(dataReceived)
                    opscode = dataDict.pop("operation", None)

                    # FOR COMPATIBILITY
                    if "node" in dataDict:
                        dataDict.update(dataDict.pop("node"))

                    if opscode == "append":
                        try:
                            loglet.append(nodes.Node(**dataDict))
                        except ValueError as error:
                            self.wfile.write("Conflict.\r\n".encode())

                    elif opscode == "read":
                        try:
                            node = loglet.read(
                                dataDict["color"],
                                dataDict["index"])
                        except ValueError:
                            self.wfile.write("Not Found.\r\n".encode())
                        except IndexError:
                            self.wfile.write("Not Found.\r\n".encode())
                        else:
                            self.wfile.write(node.encode() + b'\r\n')

                    elif opscode == "length":
                        try:
                            length = loglet.length(dataDict["color"])
                        except ValueError:
                            self.wfile.write("Not Found.\r\n".encode())
                        else:
                            self.wfile.write(str(length).encode() + b'\r\n')

                    elif opscode == "debug":
                        for color in loglet._data:
                            print("The color is: ", color)
                            for node in loglet._data[color]:
                                print(node.nid)
                                print(node.payload)
                                print(node.targets)

                    elif opscode == "over":
                        break

                except JSONDecodeError:
                    self.wfile.write("Invalid JSON.\r\n".encode())
                except KeyError as error:
                    self.wfile.write("Serialization format error ({}).\r\n".format(str(error)).encode())
                except TypeError as error:
                    self.wfile.write("Serialization format error ({}).\r\n".format(str(error)).encode())


if __name__ == "__main__":

    HOST, PORT = "localhost", 2021

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
