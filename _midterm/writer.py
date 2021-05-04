import logging
from collections import deque, namedtuple
from collections.abc import Sequence
from enum import Enum
from itertools import count
from multiprocessing import Process, Queue
from queue import Empty
from time import perf_counter, sleep

logging.basicConfig(level='INFO')

# NOTE
# Lamport Timestamp Ordering Not Implemented Yet
# Currently a proof of concept for chain serialization


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


# Suppose we have text payload, of only space and letters
# Suppose colors are a collection of Colors
LogEntry = namedtuple("LogEntry", ("colors, payload"))

# RED: A -> B -> C -> D
# GRN:                D -> E
# BLU:      X -----------> E -> Y


def fuzz():
    return 1


def client1(log):
    logging.info("S1")
    log.put(LogEntry((Color.RED, ), "A"))
    sleep(fuzz())
    log.put(LogEntry((Color.RED, ), "B"))
    sleep(fuzz())
    log.put(LogEntry((Color.RED, ), "C"))
    sleep(fuzz())
    log.put(LogEntry((Color.RED, Color.GREEN), "D"))


def client2(log):
    logging.info("S2")
    # ---
    sleep(fuzz())
    # ---
    sleep(fuzz())
    # ---
    sleep(fuzz())
    # ---
    sleep(fuzz())
    log.put(LogEntry((Color.GREEN, Color.BLUE), "E"))


def client3(log):
    logging.info("S3")
    # ---
    sleep(fuzz())
    log.put(LogEntry((Color.BLUE, ), "X"))
    sleep(fuzz())
    # ---
    sleep(fuzz())
    # ---
    sleep(fuzz())
    # ---
    sleep(fuzz())
    log.put(LogEntry((Color.BLUE, ), "Y"))


def write(file, red, green, blue):
    _red = ""
    _green = ""
    _blue = ""
    if red:
        _red = red.popleft()
    if green:
        _green = green.popleft()
    if blue:
        _blue = blue.popleft()

    file.write(",".join((_red, _green, _blue)) + '\n')


def server(queue):

    logging.info("SERVER STARTED")

    file = open('log.txt', 'w')

    red = deque()
    green = deque()
    blue = deque()

    _ts = None
    _live = True

    while _live or (red or green or blue):

        # process pending writes
        if red and green and blue:
            _ts = None
            write(file, red, green, blue)
        elif red or green or blue:
            if _ts:
                if perf_counter() - _ts > 0.5:
                    _ts = None
                    write(file, red, green, blue)
                else:
                    pass  # wait until next cycle
            else:
                _ts = perf_counter()
                # signal pending writes

        if not _live:
            continue

        try:
            item = queue.get(block=True, timeout=5)
        except Empty:
            # exit program if no input in 5 seconds
            logging.info("SERVER EXITS")
            _live = False
            continue

        if not isinstance(item, LogEntry):
            raise TypeError()
        if not isinstance(item.colors, Sequence):
            raise TypeError()
        for color in item.colors:
            if not isinstance(color, Color):
                raise TypeError()
        if not isinstance(item.payload, str):
            raise TypeError()

        for color in item.colors:
            if color == Color.RED:
                red.append(item.payload)
            elif color == Color.GREEN:
                green.append(item.payload)
            elif color == Color.BLUE:
                blue.append(item.payload)


if __name__ == '__main__':
    queue = Queue()
    Process(target=server, args=(queue, )).start()
    Process(target=client1, args=(queue, )).start()
    Process(target=client2, args=(queue, )).start()
    Process(target=client3, args=(queue, )).start()
