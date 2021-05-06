import random
import copy
import loglet
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

    request = {"operation": "add_loglet", "host":"localhost", "port":2021}
    jsonMsg = json.dumps(request) + "\n"
    dataToSend = jsonMsg.encode("utf-8")
    s.send(dataToSend)
    print(dataToSend)
    time.sleep(2)

    dataReceived_tmp = s.recv(1024).decode("utf-8")
    dataReceived = dataReceived_tmp.strip()
    print("The return text of add_loglet is: {}", dataReceived)
    time.sleep(3)
    
    ratio_of_interaction = num_of_inter_nodes / num_of_nodes
    print(ratio_of_interaction)
    remaining_inter_count = num_of_inter_nodes

    # initialize the tailMap
    tailMap = {}
    for i in range(num_of_colors):
        tailMap[colorList[i]] = 0
    
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
                target = [tailMap[colorList[index]], colorList[index]]
                targets.append(target)
                tailMap[colorList[index]] = item
            print(targets)
            remaining_inter_count -= len(color_index_set)
            num_of_nodes -= len(color_index_set)

        ## Cannot or do not need to choose interaction node
        else:
            target_color_index = random.randint(0, num_of_colors - 1)
            targets = [[tailMap[colorList[target_color_index]], colorList[target_color_index]]]
            print(targets)
            tailMap[colorList[target_color_index]] = item
            num_of_nodes -= 1

        request = {"operation": "append", "payload": "N/A", "targets": targets, "nid": item}
        jsonMsg = json.dumps(request) + "\n"
        dataToSend = jsonMsg.encode("utf-8")
        s.send(dataToSend)
        print(dataToSend)

        dataReceived_tmp = s.recv(1024).decode("utf-8")
        dataReceived = dataReceived_tmp.strip()
        print("The return text of append is: {}", dataReceived)
        time.sleep(1)
    
    return remaining_inter_count


if __name__ == "__main__":
    targetAddress = ('127.0.0.1', 9999)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.connect(targetAddress)
    #remaining_inter_count = generate_test_case(s, 3, 15, 8)

    ##############################
    num_of_colors = 3
    num_of_nodes = 9
    num_of_inter_nodes = 4
    ##############################
    request = {"operation": "add_loglet", "host":"localhost", "port":2021}
    jsonMsg = json.dumps(request) + "\n"
    dataToSend = jsonMsg.encode("utf-8")
    s.send(dataToSend)
    print(dataToSend)
    time.sleep(2)

    dataReceived_tmp = s.recv(1024).decode("utf-8")
    dataReceived = dataReceived_tmp.strip()
    print("The return text of add_loglet is: {}", dataReceived)
    time.sleep(3)
    
    ratio_of_interaction = num_of_inter_nodes / num_of_nodes
    print(ratio_of_interaction)
    remaining_inter_count = num_of_inter_nodes

    # initialize the tailMap
    tailMap = {}
    for i in range(num_of_colors):
        tailMap[colorList[i]] = 0
    
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
                target = [tailMap[colorList[index]], colorList[index]]
                targets.append(target)
                tailMap[colorList[index]] = item
            print(targets)
            remaining_inter_count -= len(color_index_set)
            num_of_nodes -= len(color_index_set)

        ## Cannot or do not need to choose interaction node
        else:
            target_color_index = random.randint(0, num_of_colors - 1)
            targets = [[tailMap[colorList[target_color_index]], colorList[target_color_index]]]
            print(targets)
            tailMap[colorList[target_color_index]] = item
            num_of_nodes -= 1

        request = {"operation": "append", "payload": "N/A", "targets": targets, "nid": item}
        jsonMsg = json.dumps(request) + "\n"
        dataToSend = jsonMsg.encode("utf-8")
        s.send(dataToSend)
        print(dataToSend)

        dataReceived_tmp = s.recv(1024).decode("utf-8")
        dataReceived = dataReceived_tmp.strip()
        print("The return text of append is: {}", dataReceived)
        time.sleep(1)

    print(remaining_inter_count)
    
    # ## print_all
    # request = {"operation": "print_all"}
    # dataToSend = json.dumps(request) + "\n".encode("utf-8")
    # s.send(dataToSend)
    # print(dataToSend)
    # time.sleep(1)

    # read
    request = {"operation": "find", "nid": 1, "color": "RED"}
    jsonMsg = json.dumps(request) + "\n"
    dataToSend = jsonMsg.encode("utf-8")
    print("The request from client is: ", dataToSend)
    s.send(dataToSend)
    #time.sleep(5)

    while True:
        dataReceived_tmp = s.recv(1024).decode("utf-8")
        dataReceived = dataReceived_tmp.strip()        
        if dataReceived:
            print(dataReceived)
            break
    # else:
    #     dataDict = json.loads(dataReceived)
    #     print(dataDict)
    #     # receivedNode = loglet.dictToNode(dataDict)
    #     # print(receivedNode)
    time.sleep(1)

    # #read_by_target
    # targetNode = []
    # request = {"operation": "read_by_target", "color": "GREEN", "target": targetNode.toDict()}
    # dataToSend = json.dumps(request) + "\n".encode("utf-8")
    # s.send(dataToSend)
    # print("The request from client is: ", dataToSend)

    # dataReceived = s.recv(1024).decode("utf-8")
    # if dataReceived == "Cannot find out the target node!":
    #     print(dataReceived)
    # else:
    #     dataDict = json.loads(dataReceived.strip())
    #     print(dataDict)
    #     # receivedNode = nodes.dictToNode(dataDict)
    #     # print(receivedNode)
    # time.sleep(1)