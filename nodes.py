from dataclasses import dataclass
from collections import defaultdict, deque
from itertools import count
from copy import deepcopy

nodes = defaultdict(list)
loglets = deque([nodes])
ids = count(1)

# -------------------
# loglet operations
# -------------------


def add_loglet():
    global nodes
    _nodes = defaultdict(list)
    loglets.append(_nodes)
    nodes = _nodes


def trim_loglet():
    loglets.popleft()


class Loglet():
    
    def __init__(self):
        self._data = defaultdict(list)

    def append(self, node):
        # if not self._data.has_key(color):
        #     raise ValueError()
        for color in node.targets:
            self._data[color].append(deepcopy(node))

    def read_by_index(self, color, index):
        if 0 <= index < len(self._data.get(color, [])):
            return self._data[color][index]
        return "Cannot find out the target node!"

    def read_by_target(self, color, node):
        if color not in self._data:
            raise ValueError()
        chain = self._data.get(color, [])
        for current in chain:
            if current.nid == node.nid:
                return current
        return "Cannot find out the target node!"

class LogIterator():

    def __init__(self, color):
        self.color = color

    def __iter__(self):
        # two pointers
        self.idx_loglet = len(loglets) - 1  # always valid
        self.idx_item = -1
        if self.idx_loglet != -1:
            self.idx_item = len(loglets[-1][self.color]) - 1
        return self

    def __next__(self):
        self._find_next()
        if self.idx_item != -1:
            loglet = loglets[self.idx_loglet]
            chain = loglet[self.color]
            _item = chain[self.idx_item]
            self.idx_item -= 1
            return _item
        else:
            raise StopIteration()

    def _find_next(self):
        # set the two pointers of the next available element to
        # a concrete position or (0, -1) indicating list exhausted

        if self.idx_loglet == 0 and self.idx_item == -1:
            return

        while not(0 <= self.idx_item < len(loglets[self.idx_loglet][self.color])):
            if self.idx_item == -1:
                self.idx_loglet -= 1
                if self.idx_loglet >= 0:
                    self.idx_item = len(loglets[self.idx_loglet][self.color]) - 1
                else:
                    self.idx_item = -1
                if self.idx_loglet == 0 and self.idx_item == -1:
                    break
            else:
                raise RuntimeError()


@dataclass
class Target:
    nid: int
    color: str


class Node():
    def __init__(self, nid=None, payload="N/A", targets=None):
        self.nid = nid or next(ids)
        self.payload = payload
        self.targets = targets or []

    def __str__(self):
        return str(self.nid)


def _appendable(target):
    if target.color in nodes and nodes[target.color]:
        return nodes[target.color][-1].nid == target.nid
    else:  # new color
        return True


def append(node, targets):
    if not all(map(_appendable, targets)):
        raise ValueError()

    node.targets = [target for target in targets if target.nid]
    for target in targets:
        nodes[target.color].append(deepcopy(node))

    # DEBUG
    # _readall()


def seek(target, _ans=None):
    chain = LogIterator(target.color)
    if _ans is None:
        _ans = []
    _targets = []
    _found = False
    for node in chain:
        if _found or node.nid == target.nid or target.nid is None:
            _found = True
            if node.nid not in _ans:
                _ans.append(node.nid)
            for _target in node.targets:
                if _target.color != target.color:
                    _targets.append(_target)
    for _target in _targets:
        seek(_target, _ans)
    return _ans


def _readall():
    print("RED")
    print(seek(Target(None, "RED")))
    print("YELLOW")
    print(seek(Target(None, "YELLOW")))
    print("GREEN")
    print(seek(Target(None, "GREEN")))
    print()

def nodeToDict(node):
    dictData = {}
    if node.nid is None:
        dictData["nid"] = "None"
    else:
        dictData["nid"] = node.nid
    dictData["payload"] = node.payload
    dictData["targets"] = node.targets
    return dictData

def dictToNode(dictionary):
    if dictionary["nid"] == "None":
        nid = None
    else:
        nid = dictionary["nid"]
    node = Node(nid, dictionary["payload"], dictionary["targets"])
    return node

#                                    (Active)
#     AAAAAAAAAAAAAAAAAAAAAAAAAA    BBBBBBBBBB
# RED 1 <- 2 <- 3 <- 6 <------ 9 <- 10 <- 13
# YEL           3 <- 7 <- 8 <- 9 <- 11
# GRE 4 <- 5 <------------8 <- 9 <- 12


def generate_test_case(num_colors, payload_size, interconnectivity_level, ratios):
    pass

# colors
# connectivity
# payload
# ratio of nodes: 3:2:1


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
    loglet.append(Node(nid = None, payload = "N/A", targets = ["RED"]))
    loglet.append(Node(nid = 1, payload = "N/A", targets = ["RED"]))
    loglet.append(Node(nid = 2, payload = "N/A", targets = ["RED"]))
    loglet.append(Node(nid = None, payload = "N/A", targets = ["YELLOW"]))
    loglet.append(Node(nid = None, payload = "N/A", targets = ["GREEN"]))
    loglet.append(Node(nid = 4, payload = "N/A", targets = ["GREEN"]))
    loglet.append(Node(nid = 3, payload = "N/A", targets = ["RED", "YELLOW"]))
    # loglet.append(Node(nid = 3, payload = "N/A", targets = ["YELLOW"]))
    loglet.append(Node(nid = 7, payload = "N/A", targets = ["YELLOW"]))
    loglet.append(Node(nid = 5, payload = "N/A", targets = ["GREEN"]))
    loglet.append(Node(nid = 8, payload = "N/A", targets = ["YELLOW", "GREEN"]))
    # loglet.append(Target(8, "GREEN"))
    loglet.append(Node(nid = 6, payload = "N/A", targets = ["RED"]))

    node = loglet.read_by_index("RED", 10)
    print(node)
    node = loglet.read_by_target("GREEN", Node(nid = 13))
    print(node)