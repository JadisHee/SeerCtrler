import socket
import json
import struct

PACK_FMT_STR = '!BBHLH6s'
IP = '192.168.0.199'

Port_State = 19204
Port_Nav = 19206

def packMasg(reqId, msgType, msg={}):
    msgLen = 0
    jsonStr = json.dumps(msg)
    if (msg != {}):
        msgLen = len(jsonStr)
    rawMsg = struct.pack(PACK_FMT_STR, 0x5A, 0x01, reqId, msgLen,msgType, b'\x00\x00\x00\x00\x00\x00')
    print("{:02X} {:02X} {:04X} {:08X} {:04X}"
    .format(0x5A, 0x01, reqId, msgLen, msgType))

    if (msg != {}):
        rawMsg += bytearray(jsonStr,'ascii')
        print(msg)

    return rawMsg


# Mod:
# 1: 执行重定位
# 2: 查询定位状态
# 3: 执行导航
# 4: 查询导航状态
def Ctrler(Mod,msg_nav={}):
    # 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if Mod==2:
        port = Port_State
        msgType = 1021
        msg = {}
    elif Mod==3:
        port = Port_Nav
        msgType = 3051
        msg = msg_nav
    elif Mod==4:
        port = Port_State
        msgType = 1020
        msg = {"simple":True}
    
    client.connect((IP,port))
    client.settimeout(5)
    send_msg = packMasg(1,msgType,msg)
    print("\n\nreq:")
    print(' '.join('{:02X}'.format(x) for x in send_msg))
    client.send(send_msg)

    dataall = b''
    # while True:
    print('\n')
    try:
        data = client.recv(16)
    except socket.timeout:
        print('timeout')
        client.close
    jsonDataLen = 0
    backReqNum = 0
    if(len(data) < 16):
        print('pack head error')
        print(data)
        client.close()
    else:
        header = struct.unpack(PACK_FMT_STR, data)
        # print("{:02X} {:02X} {:04X} {:08X} {:04X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X}       length: {}"
        # .format(header[0], header[1], header[2], header[3], header[4],
        # header[5][0], header[5][1], header[5][2], header[5][3], header[5][4], header[5][5],
        # header[3]))
        jsonDataLen = header[3]
        backReqNum = header[4]
    dataall += data
    data = b''
    readSize = 1024
    try:
        while (jsonDataLen > 0):
            recv = client.recv(readSize)
            data += recv
            jsonDataLen -= len(recv)
            if jsonDataLen < readSize:
                readSize = jsonDataLen
        print(json.dumps(json.loads(data), indent=1))
        dataall += data
        # print(' '.join('{:02X}'.format(x) for x in dataall))
    except socket.timeout:
        print('timeout')

    client.close()

if __name__ == "__main__":
    msg_nav = {"source_id": "LM2","id": "LM10"}
    Ctrler(3,msg_nav)