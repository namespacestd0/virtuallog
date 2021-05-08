# -*-coding:utf-8 -*-
# Loglet as the Server
import json
import socketserver
from argparse import ArgumentParser
from json.decoder import JSONDecodeError

from loglet import Memlet, Filelet, Node

loglet = None


class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls

        print("Connection Established: {}".format(self.client_address[0]))

        # telnet clear screen
        # self.wfile.write("\u001B[2J".encode())

        while True:
            dataReceived = self.rfile.readline()
            if not dataReceived:
                break

            dataReceived = dataReceived.strip()

            print("{} wrote:".format(self.client_address[0]))
            print(dataReceived)

            try:
                dataDict = json.loads(dataReceived)
                opscode = dataDict.pop("operation")

                # FOR COMPATIBILITY
                if "node" in dataDict:
                    dataDict.update(dataDict.pop("node"))
                # --------------------------------------

                if opscode == "append":
                    loglet.append(Node(**dataDict))
                    self._write()

                elif opscode == "read":
                    node = loglet.read(
                        dataDict["color"],
                        dataDict["index"])
                    self._write(node.to_dict())

                elif opscode == "length":
                    length = loglet.length(dataDict["color"])
                    self._write(length)

                elif opscode == "debug":
                    for color in loglet._data:
                        print(color)
                        for node in loglet._data[color]:
                            print(node.nid, node.payload, node.targets)
                    self._write()

                elif opscode == "over":
                    self._write()
                    break

            except JSONDecodeError:
                self._write_error("Invalid JSON.")
            except Exception as exc:
                self._write_error(exc)

    def _write_error(self, error):
        self._write({"success": False, "error": str(error), "type": type(error).__name__})

    def _write(self, content={"acknowledged": True}):
        if not isinstance(content, dict):
            content = {"value": content}
        self.wfile.write(json.dumps(content).encode())
        self.wfile.write("\r\n".encode())


if __name__ == "__main__":

    parser = ArgumentParser("A Loglet Server.")
    parser.add_argument("--host", dest="host", default="0.0.0.0", help="interface binding address")
    parser.add_argument("port", type=int, help="interface binding address")
    parser.add_argument("mode", choices=['mem', 'file'], help="choose loglet implementation")
    args = parser.parse_args()

    if args.mode == 'mem':
        loglet = Memlet()
    elif args.mode == 'file':
        loglet = Filelet()

    with socketserver.TCPServer((args.host, args.port), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

# {"operation": "append", "payload": "N/A",  "targets":[[null, "YELLOW"]], "nid": 1}
# {"operation": "append", "payload": "N/A",  "targets":[[1, "YELLOW"]], "nid": 2}
# {"operation": "append", "payload": "N/A",  "targets":[[2, "YELLOW"]], "nid": 3}
# {"operation": "append", "payload": "N/A",  "targets":[[3, "RED"]], "nid": 4}
# {"operation": "read","index": 0,"color":"YELLOW"}
# {"operation": "read","index": 1,"color":"YELLOW"}
# {"operation": "read","index": 100,"color":"YELLOW"}
# {"operation": "length", "color": "YELLOW"}
# {"operation": "debug"}
# {"operation": "over"}
