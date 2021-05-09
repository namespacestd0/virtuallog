import asyncio
import json
import random
import socket
import time
import uuid
from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import partial
from itertools import count

from loglet import Node, Target


class RemoteVirtualLog():

    def __init__(self, sockf, color):
        self._sockf = sockf
        self._color = color
        self.logs = []

    def _request(self, dic):
        self._sockf.write(json.dumps(dic))
        self._sockf.write('\n')
        self._sockf.flush()
        res = self._sockf.readline()
        res = json.loads(res.strip())
        assert res.get("success", True), res
        if res.get("acknowledged"):
            return
        return res

    def _find(self, nid=None):
        res = self._request({
            "operation": "find",
            "nid": nid,
            "color": self._color
        })
        node = Node(
            res["nid"],
            res["payload"],
            res["targets"]
        )
        prev_nid = None
        for target in node.targets:
            if target.color == self._color:
                prev_nid = target.nid
        return node, prev_nid

    @property
    def _nid(self):  # tail nid
        if self.logs:
            return self.logs[-1].nid
        return None

    def refresh(self):
        nid = None
        logs = []
        try:
            node, nid = self._find()
            logs = [node]
        except Exception:
            pass

        while nid:
            node, nid = self._find(nid)
            logs.append(node)

        self.logs = list(reversed(logs))

    def append(self, payload):
        node = Node(
            nid=str(uuid.uuid4())[:8],
            payload=payload,
            targets=[(self._nid, self._color)]
        )
        request = {"operation": "append"}
        request.update(**node.to_dict())
        self._request(request)
        self.logs.append(node)


class Stage(Enum):
    UNDECIDED = 0
    NEGOTIATING = 1
    AGREED = 2


class ValueNegotiator():

    QUORUM = 3

    def __init__(self, vlog):
        self.vlog = vlog
        self.voted = False
        self.result = None

    def refresh(self):
        self.vlog.refresh()

    @property
    def _values(self):
        return Counter(map(lambda node: node.payload, self.vlog.logs))

    @property
    def stage(self):

        if not self._values:
            return Stage.UNDECIDED

        value, frequency = self._values.most_common(1)[0]
        if frequency >= self.QUORUM:
            self.result = value
            return Stage.AGREED
        else:
            return Stage.NEGOTIATING

    def propose(self, value):
        assert self.stage == Stage.UNDECIDED
        self.vlog.append(value)
        self.voted = True

    def vote_for(self):
        assert self.stage == Stage.NEGOTIATING
        value, _ = self._values.most_common(1)[0]
        return value

    def vote(self):
        assert self.stage == Stage.NEGOTIATING
        value = self.vote_for()
        self.vlog.append(value)
        self.voted = True
        return value


def fuzz():
    time.sleep(random.random())
    time.sleep(random.random())
    time.sleep(random.random())


def main():
    HOST, PORT = "localhost", 9999

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.settimeout(5)
        sockf = sock.makefile('wr')
        vlog = RemoteVirtualLog(sockf, "YELLOW")
        vneg = ValueNegotiator(vlog)
        vneg.refresh()
        time.sleep(2)  # ensure we can easily simulate failure
        while True:
            fuzz()
            if vneg.stage == Stage.UNDECIDED:
                value = random.randrange(10)
                print("Proposing:", value)
                action = partial(vneg.propose, value)
            elif vneg.stage == Stage.NEGOTIATING and not vneg.voted:
                value = vneg.vote_for()
                print("Voting:", value)
                action = vneg.vote
            elif vneg.stage == Stage.AGREED:
                print("Agreed:", vneg.result)
                return
            else:
                print("Waiting for quorum.")
                vneg.refresh()
                continue
            try:
                action()
            except Exception:
                print("Failed")
                vneg.refresh()
            else:
                print("Successful")


if __name__ == "__main__":
    main()
