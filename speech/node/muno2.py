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

# 音声認識のスコアに対するしきい値
# 大きいほど認識は正確になるが、認識しずらくなる
threshoold = 0.3

# 音声認識機が反応する名前の候補（認識辞書の「ろぼっと」に対応する発音、音素表記で記載）
robot_names = [
"robo", 
"robotto", 
"oto",
"moqt"
]

def main():
	rospy.init_node('muno')

	synthesisPub = rospy.Publisher( "jtalk/sentence" , std_msgs.msg.String, queue_size=10 )
	
	rospy.wait_for_service('julius/set_grammar')
	set_grammar = rospy.ServiceProxy('julius/set_grammar', SetGrammar)
	set_grammar( gram, [] )

	rospy.set_param("/julius/robot_names", robot_names)
	rospy.set_param("/julius/recog_threshold", threshoold)


	while not rospy.is_shutdown():
		msg = rospy.wait_for_message( '/julius/recogres/small_vocab',  speech_recres )

		print( msg.sentences[0] )
		print( msg.sentence_id )

		if msg.sentence_id=="hello":
			synthesisPub.publish( "こんにちは" )
		if msg.sentence_id=="morning":
			synthesisPub.publish( "おはよう" )
		elif msg.sentence_id=="grasp":
			synthesisPub.publish( msg.noun_str[0] + "を取ります。" )
			
			# for python2
			# synthesisPub.publish( msg.noun_str[0].decode("utf8") + "を取ります。" )


if __name__ == '__main__':
	main()
