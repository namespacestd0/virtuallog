from dataclasses import dataclass
from collections import defaultdict, deque
from itertools import count

nodes = dict()
loglets = deque([nodes])
ids = count(1)

# -------------------
# loglet operations
# -------------------


def add_loglet():
    loglets.append(dict.fromkeys(nodes.keys()))


def trim_loglet():
    loglets.popleft()


@dataclass
class Target:
    nid: int
    color: str


class Loglet():
    pass


class Node():
    def __init__(self, nid=None, payload="N/A", colors=None, parents=None):
        self.nid = nid or next(ids)
        self.payload = payload
        self.colors = colors or set()
        self.parents = parents or []


def _appendable(target):
    if target.color in nodes:
        return nodes[target.color].nid == target.nid
    else:  # new color
        return True


def _append(node, target):
    if target.color in nodes:
        node.parents.append(nodes[target.color])
    if target.color not in node.colors:
        node.colors.add(target.color)
    nodes[target.color] = node


def append(node, targets):
    if not all(map(_appendable, targets)):
        raise ValueError()
    for target in targets:
        _append(node, target)
    # DEBUG
    _readall()


def _read(root):
    print(''.join(color[0] for color in root.colors), root.nid, sep='', end=' ')
    for parent in root.parents:
        _read(parent)


def read(color):
    if color in nodes:
        print(color, "\t", end=' ')
        _read(nodes[color])
        print()


def seek(target, depth=100):
    pass


def _readall():
    read("RED")
    read("YELLOW")
    read("GREEN")
    print()

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
    append(Node(), [Target(None, "RED")])
    append(Node(), [Target(1, "RED")])
    append(Node(), [Target(2, "RED"), Target(None, "YELLOW")])
    append(Node(), [Target(None, "GREEN")])
    append(Node(), [Target(4, "GREEN")])
    append(Node(), [Target(3, "RED")])
    append(Node(), [Target(3, "YELLOW")])
    append(Node(), [Target(7, "YELLOW"), Target(5, "GREEN")])
    append(Node(), [Target(8, "YELLOW"), Target(8, "GREEN"), Target(6, "RED")])
    # DEBUG
    # _readall()
