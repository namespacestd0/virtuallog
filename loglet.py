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

    def append(self, node):
        # faithfully append the node without DAG validation
        # assuming that it is performed in the upper layer
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
        return f"Node({self.nid})"

    def to_dict(self):
        return {
            "nid": self.nid,
            "payload": self.payload,
            "targets": [tuple(target) for target in self.targets]
        }
