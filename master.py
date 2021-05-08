
import asyncio
import json
from collections import deque
from dataclasses import dataclass

from loglet import Node, Target


class RemoteLogletError(Exception):
    pass


@dataclass
class RemoteLoglet():
    host: str
    port: int

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def append(self, node):
        payload = {"operation": "append"}
        payload.update(**node.to_dict())
        await self._request(payload)

    async def length(self, color):
        response = await self._request({
            "operation": "length",
            "color": color
        })
        return response["value"]

    async def read(self, color, index):
        response = await self._request({
            "operation": "read",
            "color": color,
            "index": index
        })
        return Node(**response)

    async def _request(self, dic):
        assert isinstance(dic, dict)
        self.writer.write(json.dumps(dic).encode())
        self.writer.write("\r\n".encode())
        await self.writer.drain()
        response = await self.reader.readline()
        response = json.loads(response.strip())
        if not response.get("success", True):
            raise RemoteLogletError(response.get("error"))
        return response


class LogletManager():

    def __init__(self) -> None:
        self._loglets = deque()

    # management

    async def add_loglet(self, loglet):
        await loglet.connect()
        self._loglets.append(loglet)

    async def trim_loglet(self):
        loglet = self._loglets.popleft()
        await loglet.close()

    # client

    async def _appendable(self, target):
        for loglet in reversed(self._loglets):
            length = await loglet.length(target.color)
            for index in reversed(range(length)):
                node = await loglet.read(target.color, index)
                # this is the last node of the target color
                return node.nid == target.nid
        # no conflicting record
        return True

    async def append(self, node):
        if not self._loglets:
            raise TypeError("No available loglet.")
        for target in node.targets:
            if not await self._appendable(target):
                raise ValueError("Conflict.")
        await self._loglets[-1].append(node)

    async def find(self, target):
        for loglet in reversed(self._loglets):
            length = await loglet.length(target.color)
            for index in reversed(range(length)):
                node = await loglet.read(target.color, index)
                if target.nid is None or node.nid == target.nid:
                    return node


manager = LogletManager()


def jsonify(content={"acknowledged": True}):
    if not isinstance(content, dict):
        content = {"value": content}
    return json.dumps(content).encode() + "\r\n".encode()


async def handle_request(reader, writer):

    # telnet clear screen
    writer.write("\u001B[2J".encode())
    await writer.drain()

    while True:
        message = await reader.readline()
        if not message:
            break
        message = message.strip()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        if message:
            try:
                dataDict = json.loads(message)
                opscode = dataDict.pop("operation")

                if opscode == "add_loglet":
                    await manager.add_loglet(RemoteLoglet(
                        dataDict["host"],
                        dataDict["port"]
                    ))
                    writer.write(jsonify())

                elif opscode == "trim_loglet":
                    await manager.trim_loglet()
                    writer.write(jsonify())

                elif opscode == "append":
                    await manager.append(Node(**dataDict))
                    writer.write(jsonify())

                elif opscode == "find":
                    node = await manager.find(Target(
                        dataDict["nid"],
                        dataDict["color"]
                    ))
                    if node:
                        writer.write(jsonify(node.to_dict()))
                    else:
                        raise ValueError("Not Found.")

                elif opscode == "over":
                    break

            except Exception as exc:
                writer.write(jsonify({
                    "success": False,
                    "error": str(exc)
                }))

            finally:
                await writer.drain()

    print("Close the connection")
    writer.close()


async def main():
    server = await asyncio.start_server(
        handle_request, '127.0.0.1', 9999)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

#                                    (Active)
#     AAAAAAAAAAAAAAAAAAAAAAAAAA    BBBBBBBBBB
# RED 1 <- 2 <- 3 <- 6 <------ 9 <- 10 <- 13
# YEL           3 <- 7 <- 8 <- 9 <- 11
# GRE 4 <- 5 <------------8 <- 9 <- 12


if __name__ == '__main__':
    asyncio.run(main())

# {"operation": "add_loglet", "host":"localhost", "port":2021}
# {"operation": "append", "payload": "N/A",  "targets":[[null, "RED"]], "nid": 1}
# {"operation": "append", "payload": "N/A",  "targets":[[1, "RED"]], "nid": 2}
# {"operation": "append", "payload": "N/A",  "targets":[[2, "RED"], [null, "YELLOW"]], "nid": 3}
# {"operation": "append", "payload": "N/A",  "targets":[[null, "GREEN"]], "nid": 4}
# {"operation": "append", "payload": "N/A",  "targets":[[4, "GREEN"]], "nid": 5}
# {"operation": "append", "payload": "N/A",  "targets":[[3, "RED"]], "nid": 6}
# {"operation": "append", "payload": "N/A",  "targets":[[3, "YELLOW"]], "nid": 7}
# {"operation": "append", "payload": "N/A",  "targets":[[7, "YELLOW"], [5, "GREEN"]], "nid": 8}
# {"operation": "append", "payload": "N/A",  "targets":[[6, "RED"], [8, "YELLOW"], [8, "GREEN"]], "nid": 9}
# {"operation": "add_loglet", "host":"localhost", "port":2022}
# {"operation": "append", "payload": "N/A",  "targets":[[9, "RED"]], "nid": 10}
# {"operation": "append", "payload": "N/A",  "targets":[[9, "YELLOW"]], "nid": 11}
# {"operation": "append", "payload": "N/A",  "targets":[[9, "GREEN"]], "nid": 12}
# {"operation": "find","nid": 0,"color":"YELLOW"}
# {"operation": "find","nid": 1,"color":"RED"}
# {"operation": "find","nid": 2,"color":"RED"}
# {"operation": "find","nid": 3,"color":"RED"}
# {"operation": "find","nid": 100,"color":"YELLOW"}
# {"operation": "trim_loglet"}
# {"operation": "find","nid": 2,"color":"RED"}
# {"operation": "over"}
