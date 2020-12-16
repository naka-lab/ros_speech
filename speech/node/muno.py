#!/usr/bin/python
# coding: utf-8

import rospy
import std_msgs
import os
import time
import codecs
from julius.msg import speech_recres


class muno():
	def __init__(self):
		rospy.init_node('muno')
		rospy.on_shutdown( self.shutdown )

		self.sentenceSubs = rospy.Subscriber('/julius/recogres/small_vocab',  speech_recres ,self.recieve )
		self.synthesisPub = rospy.Publisher( "jtalk/sentence" , std_msgs.msg.String, queue_size=10 )


		rospy.spin()

	def recieve(self,msg):
		print msg.sentences[0]
		print msg.sentence_id

		if msg.sentence_id=="hello":
			self.synthesisPub.publish( "こんにちは" )
		elif msg.sentence_id=="grasp":
			self.synthesisPub.publish( msg.noun_str[0] + "を取ります。" )


	def shutdown(self):
		pass

if __name__ == '__main__':
	muno()
