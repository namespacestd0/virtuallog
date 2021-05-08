import json
import random
import socket
import time
from collections import defaultdict
from itertools import count

from loglet import Node, Target

COLORS = ["RED", "GREEN", "YELLOW", "BLUE", "PINK", "WHITE", "BLACK", "GREY", "ORANGE", "PURPLE"]

# TODO weights

ids = count(1)


def generate_test_cases(num_of_colors=5, num_of_nodes=1000, single_color_factor=0.7):

    # lower bound is set so that multicolor
    # factor parameter is always meaningful
    assert 2 <= num_of_colors <= 10
    # we only have 10 pre-defined colors

    ans = []
    ref = defaultdict(list)
    colors = list(COLORS[:num_of_colors])

    for _ in range(num_of_nodes):
        if random.random() < single_color_factor:
            _targets = [random.choice(colors)]
        else:  # this node has multiple colors
            _targets = random.sample(colors, random.randrange(2, len(colors)))

        def targetify(color):
            last_one = None
            if ref[color]:
                last_one = ref[color][-1].nid
            return Target(last_one, color)

        targets = list(map(targetify, _targets))
        node = Node(str(next(ids)), targets=targets)
        for target in targets:
            ref[target.color].append(node)
        ans.append(node)

    return ans


def generate_test_request(testcase):
    request = testcase.to_dict()
    request["operation"] = "append"
    return (json.dumps(request) + '\n').encode()


def _assert(res):
    res = json.loads(res.strip())
    assert res["acknowledged"]


if __name__ == "__main__":

    HOST, PORT = "localhost", 9999

    print("CONNECTING...")

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.settimeout(5)
        sockf = sock.makefile('wr')

        sock.recv(1024)  # clear telnet command

        sockf.write(json.dumps({"operation": "add_loglet", "host": "localhost", "port": 2021}))
        sockf.write('\n')
        sockf.flush()

        _assert(sockf.readline())
        print("SENDING REQUESTS...")

        testcases = generate_test_cases()
        t0 = time.time()
        for testcase in testcases:
            request = generate_test_request(testcase)
            sock.sendall(request)

        print("VALIDATING RESULTS...")

        while True:
            try:
                response = sockf.readline()
            except OSError:
                break
            if not response:
                break
            _assert(response)

        print("TOTAL TIME:", time.time() - t0 - 5)
