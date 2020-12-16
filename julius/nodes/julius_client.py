# coding: utf-8

import socket
import threading
import re
import sys
import os
import codecs

JULIUS_STATUS_RECOGSTART = 0
JULIUS_STATUS_RECOGEND = 1
JULIUS_STATUS_RECOGFAIL = 2
JULIUS_STATUS_REJECTED = 3

class JuliusRecogResult():
    def __init__(self):
        self.sentence = ""
        self.phone = ""
        self.score = 0.0
        self.words = []
        self.classIDs = []

class JuliusClient():
    def RecieveThread( client ):
        data = ""        
        while client.isAlive:
            data += client.soc.recv(1)

            if not data:
                     break

            # データの区切りを見つける
            pos = data.find( "\n." )
            if pos!=-1:
                packet = data[:pos]
                data = data[pos+2:]

                client.ParsePacket( packet )

    def __init__( self ):
        self.soc = None
        self.isAlive = False        
        self.recvThread = None
        self.recogResutls = []
        self.statusChangeEvent = threading.Event()
        self.status = JULIUS_STATUS_RECOGEND


    def connect( self, port ):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect(("localhost", port ))
        self.isAlive = True
        self.recvThread = threading.Thread(target=JuliusClient.RecieveThread, args=(self,))
        #self.recvThread.deamon = True
        self.recvThread.start()

    def disconnect():
        self.isAlive = False
        self.soc.close()


    def ParsePacket( self, packet ):
        # 状態の変化を受信した場合
        packet = packet.decode("utf8")
        status = re.findall( u'''INPUT STATUS="(\S+?)"''' , packet )
        if len(status)==1 and status[0]=="STARTREC":
            #print "認識開始"
            self.status = JULIUS_STATUS_RECOGSTART
            self.statusChangeEvent.set()             
            return
                         
        
        # 認識に失敗した場合
        if packet.find("<RECOGFAIL/>")!=-1:
            self.status = JULIUS_STATUS_RECOGFAIL
            self.statusChangeEvent.set()
            #print "認識失敗"
            return
        elif packet.find("<REJECTED")!=-1:
            self.status = JULIUS_STATUS_REJECTED
            self.statusChangeEvent.set()
            #print "入力棄却"
            return

        # 認識結果を受信した場合
        if packet.find("<RECOGOUT>")!=-1:
            self.recogResutls = []
            for res in packet.split("</SHYPO>"):                 
                words = re.findall('''WORD="(.*?)"''' , res)
                phones = re.findall('''PHONE="(.*?)"''' , res)
                classIDs = re.findall('''CLASSID="(.*?)"''' , res)
                
                r = JuliusRecogResult()
                for i in range(len(words)):
                    r.sentence += words[i]
                    r.phone += phones[i] + " "

                r.classIDs = classIDs
                r.words = words
                r.phones = phones

                self.recogResutls.append( r )

                #print r.sentence
                #print r.phone
            #print "認識終了"
            self.status = JULIUS_STATUS_RECOGEND
            self.statusChangeEvent.set()
            return


    def WaitForRecognized(self):
        self.statusChangeEvent.wait()
        self.statusChangeEvent.clear()
        return self.status

    def GetRecogResults(self):
        return self.recogResutls

    def GetStatus(self):
        return self.status

    def SendCommand(self, com ):         
        #print com, len(com)
        self.soc.sendall( com.encode("utf8") )
        if  com[-1]!="\n":
             self.soc.sendall("\n")

    def ChangeGram( self, filename ):
        dfafile = filename + ".dfa" 
        dictfile = filename + ".dict"


        packet = "CHANGEGRAM gram\n"
        packet += codecs.open( dfafile , "r" , "utf8" ).read()
        packet += "\nDFAEND\n"
        packet += codecs.open( dictfile , "r" , "utf8" ).read()
        packet += "\nDICEND\n"

        self.SendCommand( packet )





if __name__ == "__main__":
    j = JuliusClient()
    j.connect( 10002 )
    
    while 1:
        com = raw_input("enter")
        j.ChangeGram( "test" )





