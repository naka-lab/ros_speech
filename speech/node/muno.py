#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals
import rospy
import std_msgs
import os
import time
import codecs
from julius.msg import speech_recres
from julius.srv import SetGrammar

# 音声認識辞書
gram = """
[GRAMMAR]
hello : ろぼっと、こんにちわ
morning : ろぼっと、おはよう
grasp : ろぼっと、 $noun_obj をとって
noise : つ


[NOUN]
$noun_obj
obj1 : ぬいぐるみ
obj2 : おちゃ
obj3 : ぺっとぼとる

"""



class muno():
	def __init__(self):
		rospy.init_node('muno')
		rospy.on_shutdown( self.shutdown )

		self.sentenceSubs = rospy.Subscriber('/julius/recogres/small_vocab',  speech_recres ,self.recieve )
		self.synthesisPub = rospy.Publisher( "jtalk/sentence" , std_msgs.msg.String, queue_size=10 )
		
		rospy.wait_for_service('julius/set_grammar')
		set_grammar = rospy.ServiceProxy('julius/set_grammar', SetGrammar)
		set_grammar( gram, [] )


		rospy.spin()

	def recieve(self,msg):
		print( msg.sentences[0] )
		print( msg.sentence_id )

		if msg.sentence_id=="hello":
			self.synthesisPub.publish( "こんにちは" )
		if msg.sentence_id=="morning":
			self.synthesisPub.publish( "おはよう" )
		elif msg.sentence_id=="grasp":
			# for python3
                        self.synthesisPub.publish( msg.noun_str[0] + "を取ります。" )
                        
                        # for python2
                        # self.synthesisPub.publish( msg.noun_str[0].decode("utf8") + "を取ります。" )


	def shutdown(self):
		pass

if __name__ == '__main__':
	muno()
