
import asyncio
from dataclasses import dataclass
import json
from collections import deque
from typing_extensions import final


@dataclass
class RemoteLoglet():
    host: str
    port: int

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    def append(self, color, node):
        pass

    def read(self, color, index):
        pass

    def find(self, target):
        pass


class LogletManager():

    def __init__(self) -> None:
        self._loglets = deque()
        # fault tolarance?

    # management

    async def add_loglet(self, loglet):
        await loglet.connect()
        self._loglets.append(loglet)

    async def trim_loglet(self):
        loglet = self._loglets.popleft()
        await loglet.close()

    # client

    def append(self, color, node):
        pass

    def read(self, color, index):
        pass

    def find(self, target):
        pass


manager = LogletManager()


async def handle_echo(reader, writer):

    while True:

        data = await reader.readline()
        message = data.decode().strip()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        # -------------------------------------------------

        if not message:
            continue
        if message.upper() == 'EXIT':
            break

        if message.upper().startswith("ADD"):
            splits = data.split()
            if not len(splits) == 3:
                writer.write('Invalid command.'.encode())
                continue
            try:
                loglet = RemoteLoglet(splits[1], splits[2])
                await loglet.connect()
            except Exception:
                pass
            else:
                manager.add_loglet(loglet)

        elif message.upper().startswith("TRIM"):
            try:
                pass
            except BaseException:
                pass
            else:
                pass
            finally:
                manager.trim_loglet()

        elif message.upper().startswith("FIND"):
            pass
        else:
            pass

        # -------------------------------------------------

        print(f"Send: {message!r}")
        writer.write(data)
        await writer.drain()

    print("Close the connection")
    writer.close()


async def main():
    server = await asyncio.start_server(
        handle_echo, '127.0.0.1', 9999)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

# class LogIterator():

#     def __init__(self, color):
#         self.color = color

#     def __iter__(self):
#         # two pointers
#         self.idx_loglet = len(loglets) - 1  # always valid
#         self.idx_item = -1
#         if self.idx_loglet != -1:
#             self.idx_item = len(loglets[-1][self.color]) - 1
#         return self

#     def __next__(self):
#         self._find_next()
#         if self.idx_item != -1:
#             loglet = loglets[self.idx_loglet]
#             chain = loglet[self.color]
#             _item = chain[self.idx_item]
#             self.idx_item -= 1
#             return _item
#         else:
#             raise StopIteration()

#     def _find_next(self):
#         # set the two pointers of the next available element to
#         # a concrete position or (0, -1) indicating list exhausted

#         if self.idx_loglet == 0 and self.idx_item == -1:
#             return

#         while not(0 <= self.idx_item < len(loglets[self.idx_loglet][self.color])):
#             if self.idx_item == -1:
#                 self.idx_loglet -= 1
#                 if self.idx_loglet >= 0:
#                     self.idx_item = len(loglets[self.idx_loglet][self.color]) - 1
#                 else:
#                     self.idx_item = -1
#                 if self.idx_loglet == 0 and self.idx_item == -1:
#                     break
#             else:
#                 raise RuntimeError()

# def seek(target, _ans=None):
#     chain = LogIterator(target.color)
#     if _ans is None:
#         _ans = []
#     _targets = []
#     _found = False
#     for node in chain:
#         if _found or node.nid == target.nid or target.nid is None:
#             _found = True
#             if node.nid not in _ans:
#                 _ans.append(node.nid)
#             for _target in node.targets:
#                 if _target.color != target.color:
#                     _targets.append(_target)
#     for _target in _targets:
#         seek(_target, _ans)
#     return _ans

if __name__ == '__main__':
    asyncio.run(main())
