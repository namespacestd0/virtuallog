import json
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass
from itertools import count
from collections import namedtuple

ids = count(1)

Target = namedtuple('Target', ('nid', 'color'))


class Loglet():

    def __init__(self):
        self._data = defaultdict(list)

    def _appendable(self, target):
        if target.color in self._data and self._data[target.color]:
            return self._data[target.color][-1].nid == target.nid
        else:  # new color
            return True

    def append(self, node):
        if not all(map(self._appendable, node.targets)):
            raise ValueError("Conflict.")
        for target in node.targets:
            self._data[target.color].append(deepcopy(node))

    def read(self, color, index):
        return self._data[color][index]

    def length(self, color):
        return len(self._data.get(color, []))


class Node():
    def __init__(self, nid=None, payload="N/A", targets=None):
        self.nid = nid or next(ids)
        self.payload = payload
        self.targets = targets or []
        self.targets = [Target(*target) for target in self.targets]

    def __str__(self):
        return str(self.nid)

    def encode(self):
        return json.dumps({
            "nid": self.nid,
            "payload": self.payload,
            "targets": [tuple(target) for target in self.targets]
        }).encode()


def _readall():
    print("RED")
    print(seek(Target(None, "RED")))
    print("YELLOW")
    print(seek(Target(None, "YELLOW")))
    print("GREEN")
    print(seek(Target(None, "GREEN")))
    print()


#                                    (Active)
#     AAAAAAAAAAAAAAAAAAAAAAAAAA    BBBBBBBBBB
# RED 1 <- 2 <- 3 <- 6 <------ 9 <- 10 <- 13
# YEL           3 <- 7 <- 8 <- 9 <- 11
# GRE 4 <- 5 <------------8 <- 9 <- 12


if __name__ == '__main__':
    # append(Node(), [Target(None, "RED")])
    # append(Node(), [Target(1, "RED")])
    # append(Node(), [Target(2, "RED"), Target(None, "YELLOW")])
    # append(Node(), [Target(None, "GREEN")])
    # append(Node(), [Target(4, "GREEN")])
    # append(Node(), [Target(3, "RED")])
    # append(Node(), [Target(3, "YELLOW")])
    # append(Node(), [Target(7, "YELLOW"), Target(5, "GREEN")])
    # append(Node(), [Target(8, "YELLOW"), Target(8, "GREEN"), Target(6, "RED")])
    # # DEBUG
    # _readall()
    # add_loglet()
    # append(Node(), [Target(9, "RED")])
    # append(Node(), [Target(9, "YELLOW")])
    # append(Node(), [Target(9, "GREEN")])
    # append(Node(), [Target(10, "RED")])
    # # DEBUG
    # _readall()
    # trim_loglet()
    # # DEBUG
    # _readall()

    # Test of Loglet class
    loglet = Loglet()
    loglet.append(Node(nid=None, payload="N/A", targets=["RED"]))
    loglet.append(Node(nid=1, payload="N/A", targets=["RED"]))
    loglet.append(Node(nid=2, payload="N/A", targets=["RED"]))
    loglet.append(Node(nid=None, payload="N/A", targets=["YELLOW"]))
    loglet.append(Node(nid=None, payload="N/A", targets=["GREEN"]))
    loglet.append(Node(nid=4, payload="N/A", targets=["GREEN"]))
    loglet.append(Node(nid=3, payload="N/A", targets=["RED", "YELLOW"]))
    # loglet.append(Node(nid = 3, payload = "N/A", targets = ["YELLOW"]))
    loglet.append(Node(nid=7, payload="N/A", targets=["YELLOW"]))
    loglet.append(Node(nid=5, payload="N/A", targets=["GREEN"]))
    loglet.append(Node(nid=8, payload="N/A", targets=["YELLOW", "GREEN"]))
    # loglet.append(Target(8, "GREEN"))
    loglet.append(Node(nid=6, payload="N/A", targets=["RED"]))

    node = loglet.read_by_index("RED", 10)
    print(node)
    node = loglet.read_by_target("GREEN", Node(nid=13))
    print(node)
