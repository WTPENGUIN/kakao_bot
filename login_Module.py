#-*-coding:utf-8-*-
import sys
import socket
from time import sleep

def isAuth(input_ID, input_PW):

    # 소켓 통신 변수
    
    HOST = "127.0.0.1"
    PORT = 7000

    # 접속시도
    try:
        auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        auth_socket.connect((HOST, PORT))

    # 예외처리
    except Exception as e:
        print (e)
        return -2

    # ID, PASS 전송
    message = input_ID + ':' + input_PW + ':1'
    auth_socket.send(message.encode())

    try:
        read = auth_socket.recv(1024)
        if('FAIL' in read.decode()):
            auth_socket.close()
            return -1
        else:
            auth_socket.close()
            return 1
    except:
        return -2
