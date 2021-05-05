import random
import copy
import nodes
import socket
import json
import time

colorList = ["RED", "GREEN", "YELLOW", "BLUE", "PINK", "WHITE", "BLACK", "GREY", "ORANGE", "PURPLE"]

'''

3, 2/9, 9
red:   -> A -> D ----------->
green: -> C -> D -> F -> I ->
blue:  -> B ------> G -> I ->

'''

def generate_test_case (socket = None, num_of_colors = 3, num_of_nodes = 9, num_of_inter_nodes = 4):
    s = socket
    
    ratio_of_interaction = num_of_inter_nodes / num_of_nodes
    print(ratio_of_interaction)
    remaining_inter_count = num_of_inter_nodes

    item = 0
    while num_of_nodes > 0:
        item += 1
        is_interaction = random.random() < 0.5

        ## Need to choose interaction node
        if is_interaction == True and remaining_inter_count >= 2:
            ## size of this interaction node
            inter_size = min(num_of_nodes, remaining_inter_count, random.randint(2, num_of_colors))
            ## the index of colors in colorList
            color_index_set = random.sample(range(0, num_of_colors), inter_size)
            targets = []
            for index in color_index_set:
                targets.append(colorList[index])
            print(targets)
            remaining_inter_count -= len(color_index_set)
            num_of_nodes -= len(color_index_set)

        ## Cannot or do not need to choose interaction node
        else:
            target_color_index = random.randint(0, num_of_colors - 1)
            targets = [colorList[target_color_index]]
            print(targets)
            #heads_list[target_color_index].append(item, [], target_color_index)
            num_of_nodes -= 1

        node = nodes.Node(nid = item, payload = "N/A", targets = targets)
        request = {"operation": "append", "node": nodes.nodeToDict(node)}
        dataToSend = json.dumps(request).encode("utf-8")
        s.send(dataToSend)
        print(dataToSend)
        time.sleep(1)
    
    return remaining_inter_count


if __name__ == "__main__":
    targetAddress = ('172.22.157.18', 2021)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.connect(targetAddress)
    remaining_inter_count = generate_test_case(s, 3, 15, 8)
    print(remaining_inter_count)
    
    ## print_all
    request = {"operation": "print_all"}
    dataToSend = json.dumps(request).encode("utf-8")
    s.send(dataToSend)
    print(dataToSend)
    time.sleep(1)

    ## read_by_index
    request = {"operation": "read_by_index", "color": "RED", "index": 1}
    dataToSend = json.dumps(request).encode("utf-8")
    s.send(dataToSend)
    print("The request from client is: ", dataToSend)

    dataReceived = s.recv(1024).decode("utf-8")
    if dataReceived == "Cannot find out the target node!":
        print(dataReceived)
    else:
        dataDict = json.loads(dataReceived)
        print(dataDict)
        receivedNode = nodes.dictToNode(dataDict)
        print(receivedNode)
    time.sleep(1)

    #read_by_target
    targetNode = nodes.Node(nid = 3)
    request = {"operation": "read_by_target", "color": "GREEN", "target": nodes.nodeToDict(targetNode)}
    dataToSend = json.dumps(request).encode("utf-8")
    s.send(dataToSend)
    print("The request from client is: ", dataToSend)

    dataReceived = s.recv(1024).decode("utf-8")
    if dataReceived == "Cannot find out the target node!":
        print(dataReceived)
    else:
        dataDict = json.loads(dataReceived)
        print(dataDict)
        receivedNode = nodes.dictToNode(dataDict)
        print(receivedNode)
    time.sleep(1)