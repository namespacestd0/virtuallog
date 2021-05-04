
from writer import Color


def read(color):
    file = open('log.txt', 'r')
    index = slice(0, 0)
    if color == Color.RED:
        index = 0
    elif color == Color.GREEN:
        index = 1
    elif color == Color.BLUE:
        index = 2

    for line in file:
        line = line.strip('\n')
        nodes = line.split(',')
        node = nodes[index]
        print(node, end='')
    print()


if __name__ == '__main__':
    read(Color.RED)
    read(Color.GREEN)
    read(Color.BLUE)
