# encoding: shift_jis
import os
import socket
import time
import sys

def Recog( port ):
    # julius起動
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(("localhost", port ))

    while 1:
        data = soc.recv(1024)
        print data,

        if not data:
            break
    soc.close()


def main():
    Recog( int(sys.argv[1]) )

if __name__ == '__main__':
    main()