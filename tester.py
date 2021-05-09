import json
import random
import socket
import time
from collections import defaultdict
from itertools import count
from argparse import ArgumentParser

from loglet import Node, Target

COLORS = ["RED", "GREEN", "YELLOW", "BLUE", "PINK", "WHITE", "BLACK", "GREY", "ORANGE", "PURPLE"]


def generate_test_cases(num_of_colors=5, num_of_nodes=1000, single_color_factor=0.7):

    # lower bound is set so that multicolor
    # factor parameter is always meaningful
    assert 2 <= num_of_colors <= 10
    # we only have 10 pre-defined colors

    ans = []
    ids = count(1)
    ref = defaultdict(list)
    colors = list(COLORS[:num_of_colors])

    for _ in range(num_of_nodes):

        # generate targets
        if random.random() < single_color_factor:
            _targets = [random.choice(colors)]
        else:  # this node has multiple colors
            _targets = random.sample(colors, random.randrange(2, len(colors) + 1))

        def targetify(color):
            last_one = None
            if ref[color]:
                last_one = ref[color][-1].nid
            return Target(last_one, color)

        targets = list(map(targetify, _targets))
        node = Node(str(next(ids)), targets=targets)

        # maintain DAG tail view reference
        for target in targets:
            ref[target.color].append(node)
        ans.append(node)

    return ans


class VirtualLogTester():

    def __init__(self, sockf):
        self.sockf = sockf

    @staticmethod
    def _assert(res):
        res = json.loads(res.strip())
        assert res.get("acknowledged"), res

    def prepare(self, host="localhost", port=2021):
        self.sockf.write(json.dumps({
            "operation": "add_loglet",
            "host": host,
            "port": port}))
        self.sockf.write('\n')
        self.sockf.flush()
        self._assert(self.sockf.readline())

    def finished(self):
        self.sockf.write(json.dumps({
            "operation": "trim_loglet",
        }))
        self.sockf.write('\n')
        self.sockf.flush()
        self._assert(self.sockf.readline())

    def write_all(self, nodes):
        t0 = time.time()
        for node in nodes:
            request = node.to_dict()
            request["operation"] = "append"
            self.sockf.write(json.dumps(request))
            self.sockf.write('\n')
            self.sockf.flush()
            self._assert(self.sockf.readline())
        return time.time() - t0

    def read_all(self, nodes):
        t0 = time.time()
        for node in nodes:
            request = {
                "operation": "find",
                "nid": node.nid,
                "color": random.choice(node.targets).color
            }
            self.sockf.write(json.dumps(request))
            self.sockf.write('\n')
            self.sockf.flush()
            res = self.sockf.readline()
            res = json.loads(res.strip())
            assert res["nid"] == node.nid
        return time.time() - t0


def test_1(sockf, args):
    testcases = generate_test_cases(args.colors, args.nodes, args.singles)
    tester = VirtualLogTester(sockf)
    tester.prepare()
    print("WRITING TO VIRTUALLOG...")
    print("WRITE TIME:", tester.write_all(testcases))
    print("VALIDATING RESULTS...")
    print("READ TIME:", tester.read_all(random.sample(testcases, args.reads)))
    tester.finished()


def test_2(sockf, args):
    testcases = generate_test_cases(args.colors, args.nodes, args.singles)
    x = len(testcases) // 9  # individual segment length

    tester = VirtualLogTester(sockf)
    write_time = []
    read_time = []
    cread_time = []  # cumulative

    for round in range(3):
        print(f"ROUND [{round + 1}/3]")
        if round == 0:
            tester.prepare(port=2021)
        elif round == 1:
            tester.prepare(port=2022)
        else:
            tester.finished()  # close the first loglet

        for offset in range(3):
            n = round * 3 + offset  # multiplier
            t = tester.write_all(testcases[n * x: (n + 1) * x])
            print("WRITE TIME:", t)
            write_time.append(t)
            t = tester.read_all(random.sample(testcases[n * x: (n + 1) * x], args.reads))
            print("READ TIME:", t)
            read_time.append(t)
            if round < 2:
                t = tester.read_all(random.sample(testcases[: (n + 1) * x], args.reads))
            else:  # last round doesn't have the first segment available
                t = tester.read_all(random.sample(testcases[3 * x: (n + 1) * x], args.reads))
            print("CUMULATIVE READ:", t)
            cread_time.append(t)

    tester.finished()  # close the second loglet

    print()
    print("SUMMARY")
    print("WRITE:", write_time)
    print("READ:", read_time)
    print("CUMR:", cread_time)


def main():
    HOST, PORT = "localhost", 9999

    parser = ArgumentParser("A VirtualLog Tester.")
    parser.add_argument("--colors", type=int, default=5)
    parser.add_argument("--singles", type=float, default=0.7)
    parser.add_argument("--nodes", type=int, default=1000)
    parser.add_argument("--reads", type=int, default=100)
    args = parser.parse_args()

    print("CONNECTING...")
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.settimeout(5)
        sockf = sock.makefile('wr')
        # sock.recv(1024)  # clear telnet command

        # test_1(sockf, args)
        test_2(sockf, args)


if __name__ == "__main__":
    main()
