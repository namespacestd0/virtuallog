import json
from collections import defaultdict, namedtuple
from copy import deepcopy
from itertools import count
from os import path

ids = count(1)  # only used for dev purposes

Target = namedtuple('Target', ('nid', 'color'))


class Node():
    def __init__(self, nid=None, payload="N/A", targets=None):
        self.nid = nid or next(ids)
        self.payload = payload
        self.targets = targets or []
        self.targets = [Target(*target) for target in self.targets]

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "nid": self.nid,
            "payload": self.payload,
            "targets": [tuple(target) for target in self.targets]
        }


class Loglet():

    def append(self, node):
        raise NotImplementedError

    def length(self, color):
        raise NotImplementedError

    def read(self, color, index):
        raise NotImplementedError


class Memlet(Loglet):

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


class Filelet(Loglet):

    def __init__(self, root='./_tmp'):
        assert path.isdir(root)
        self._root = root

    def _build_path(self, color):
        return path.join(self._root, color + '.txt')

    def append(self, node):
        record = json.dumps(node.to_dict())
        for target in node.targets:
            with open(self._build_path(target.color), 'a') as file:
                file.write(record)
                file.write("\n")

    def length(self, color):
        _path = self._build_path(color)
        cnt = 0
        if path.exists(_path):
            with open(_path) as file:
                while file.readline():
                    cnt += 1
        return cnt

    def read(self, color, index):
        if not 0 <= index < self.length(color):
            raise IndexError()
        with open(self._build_path(color)) as file:
            _index = -1
            while _index != index:
                record = file.readline()
                _index += 1
            return Node(**json.loads(record))
