#!/usr/bin/env python
# coding: utf-8

import rospy
import os
import jtalk.srv
import std_msgs.msg


class OpenJTalk():
    def __init__(self):
        rospy.on_shutdown(self.shutdown)
        rospy.Subscriber("jtalk/sentence", std_msgs.msg.String, self.say)
        rospy.Service("jtalk/say", jtalk.srv.Say, self.say)
        self._open_jtalk_script = os.path.join(
            os.path.dirname(__file__), "openjtalk.sh")

    def say(self,req):
        if isinstance(req, jtalk.srv.SayRequest):
            rospy.loginfo("{req.sentence} を発話".format(**locals()))
            cmd = "{self._open_jtalk_script} {req.sentence}".format(**locals())
            try:
                os.system(cmd)
            except (Exception) as e:
                rospy.logerr(e)
                return jtalk.srv.SayResponse(False)
            else:
                return jtalk.srv.SayResponse(True)
        elif isinstance(req, std_msgs.msg.String):
            rospy.loginfo("{req.data} を発話".format(**locals()))
            cmd = "{self._open_jtalk_script} {req.data}".format(**locals())
            os.system(cmd)


    def shutdown(self):
        pass

if __name__ == '__main__':
    rospy.init_node('jtalk')

    OpenJTalk()

    rospy.spin()
