#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals
import rospy
import std_msgs
import julius_client
import os
import time
import codecs
import DPMatching
from julius.msg import speech_recres
from julius.srv import *
import ConvGramToJulius
HOME = os.getenv("HOME")
PATH = os.path.dirname(__file__)
os.chdir(PATH)


############ 設定 #####################
score_threshold = 0.3
robot_names = [
"robo", 
"robotto",
"oto",
"moqt"
]
#######################################

class JuliusRecognizer():
    def __init__(self):
        
        #nodeName = rospy.get_param("~node_name" , "julius_largevocab" )
  
        rospy.init_node("SpeechRecognition")
        rospy.on_shutdown( self.shutdown )

        rospy.Subscriber('julius/grammar',  std_msgs.msg.String ,self.change_grammaer )
        rospy.Service( "julius/set_grammar" , SetGrammar, self.set_gammar )

        self.pub_recogres_lv = rospy.Publisher('julius/recogres/large_vocab', speech_recres , queue_size=10)
        self.pub_recogres_sv = rospy.Publisher('julius/recogres/small_vocab', speech_recres , queue_size=10)
        

        print( "execute" )
        os.system( "Julius/KillJulius.sh" )
        os.system( "Julius/LargeVocab.sh &" )
        os.system( "Julius/SmallVocab.sh &" )        
        
        time.sleep( 5 )
        print( "connect" )
        self.__jLargeVocab = julius_client.JuliusClient()
        self.__jLargeVocab.connect( 10000 )
        
        self.__jSmallVocab = julius_client.JuliusClient()
        self.__jSmallVocab.connect( 10002 )
        
        # 辞書送信
        req = SetGrammarRequest()
        req.grammar = codecs.open("sample.txt", "r", "utf8").read()
        self.set_gammar( req )
        self.__valid_gram_id = []

        # パラメータのデフォル値を設定
        if not rospy.has_param( "/julius/robot_names" ):
            print("set")
            rospy.set_param( "/julius/robot_names", robot_names )
        if not rospy.has_param( "/julius/recog_threshold" ):
            print("set")
            rospy.set_param( "/julius/recog_threshold", score_threshold )


        self.main_loop()
  
        os.system( "Julius/KillJulius.sh" )
        
        
    def main_loop(self):
        global robot_names, score_threshold
        while not rospy.is_shutdown():
            if self.__jLargeVocab.WaitForRecognized()==julius_client.JULIUS_STATUS_RECOGEND:
                # パラメータ取得
                robot_names = rospy.get_param("/julius/robot_names")
                score_threshold = rospy.get_param( "/julius/recog_threshold" )

                largeVocabRes = self.__jLargeVocab.GetRecogResults()
                print( "*** 大語彙認識 ***" )
                print( largeVocabRes[0].sentence )
                res = speech_recres()
                for lvr in largeVocabRes:
                    sentence = lvr.sentence.replace("<s>","").replace("</s>","")
                    res.sentences.append( sentence )
                self.pub_recogres_lv.publish( res )
                    

                if self.__jSmallVocab.WaitForRecognized()==julius_client.JULIUS_STATUS_RECOGEND:
                    smallVocabRes = self.__jSmallVocab.GetRecogResults()
                    print( "*** 少語彙認識 ***" )
                    print( smallVocabRes[0].sentence.replace("<s>","").replace("</s>","") )
                    if self.is_valid( largeVocabRes, smallVocabRes ):
                        os.system( "aplay beep_success.wav" )
                        self.publish_small_vocab_results( smallVocabRes )
                    
  
    def publish_small_vocab_results(self, smallVocabRes):
        gram_id = ConvGramToJulius.GetGramID( smallVocabRes[0].classIDs )
        noun_ids, noun_strs = ConvGramToJulius.GetNounID( smallVocabRes[0].classIDs, smallVocabRes[0].words )

        res = speech_recres()
        
        res.sentences.append( smallVocabRes[0].sentence.replace("<s>","").replace("</s>","") )
        res.noun_id = noun_ids
        res.noun_str = noun_strs
        res.sentence_id = gram_id
        
        print( res.sentences )
        print( r"sentenceid:",res.sentence_id )
        print( r"nounid:",res.noun_id )
        print( r"nounstr:",res.noun_str )
        self.pub_recogres_sv.publish( res )

    def normalize_phone( self, phone ):
        phone = phone.replace("silE", "" ).replace( "silB" , "" )
        while " " in phone:
            phone = phone.replace(" " , "" ) 
        return phone       
    
    def set_gammar( self, req ):
        if len(req.grammar):
            print( "辞書更新" ) 
            #if type(req.grammar)!=unicode:
            #    gra = req.grammar.decode("utf8")
            #else:
            #    gra = req.grammar
            gra = req.grammar
            try:
                gra = gra.decode("utf8")
            except:
                pass
            f = codecs.open( "temp.txt" , "w", "utf8" )
            f.write(gra)
            f.close()
            
            succes = ConvGramToJulius.CompileGrammar( "temp.txt" , "temp" )
            
            if not succes:
                return SetGrammarResponse( False )
                
            f_dfa = codecs.open( "temp.dfa" , "r" , "utf8" )
            f_dic = codecs.open( "temp.dict" , "r" , "utf8" )
            
            packet = "CHANGEGRAM gram\n"
            packet += f_dfa.read()
            packet += "\nDFAEND\n"
            packet += f_dic.read()
            packet += "\nDICEND"
            
            f_dfa.close()
            f_dic.close()
            
            print( "辞書送信" )
            self.__jSmallVocab.SendCommand( packet )
            
        self.__valid_gram_id = []
        if self.__valid_gram_id:
            self.__valid_gram_id = req.valid_gram_id
        
        return SetGrammarResponse( True )
        
        

    def is_valid( self, largeVocabRes, smallVocabRes ):
        lphone =  self.normalize_phone( largeVocabRes[0].phone )
        sphone =  self.normalize_phone( smallVocabRes[0].phone )
        
        if len(lphone)==0 or len(sphone)==0:
            return False

        print( "大語彙比較：",lphone , "-" , sphone, )
       
        score = 1-DPMatching.levenshtein_distance( lphone , sphone )[0]/ float(max( (len(lphone), len(sphone)) ))
        print( " -> ", score, )
        if score < score_threshold:
            print( "Rejected" )
            return
        print( "Accepted" )
        print( )

        print( "ロボット名検証", )
        for name in robot_names:
            length = len(name)
            name_recog = lphone[:length]
            
            score = 1-DPMatching.levenshtein_distance( name , name_recog )[0]/ float(max( (len(name), len(name_recog)) ))
            print( name_recog, "-", name, score )
            
            if score>0.5:
                print( "Accepted" )
                return True
            
            print( "Rejected" )
        return False
            
                    

    def change_grammaer(self,msg):
        print( msg.data  )
        f = codecs.open("tmpgram.txt" , "w" , "utf8")
        f.write(msg.data)
        f.close()

        try:
            os.remove( "tmp.dfa" )
            os.remove( "tmp.dict" )
        except:
            pass

        os.system("python ConvGramToJulius.py tmpgram.txt tmp")
        os.system("mkdfa.pl tmp")

        if os.path.exists("tmp.dfa") and os.path.exists("tmp.dict"):
            self.julius.Send

    def shutdown(self):
        os.system("Julius/KillJulius.sh")
        self.__jLargeVocab.disconnect()
        self.__jSmallVocab.disconnect()

if __name__ == '__main__':
    # julius の準備
    JuliusRecognizer()
