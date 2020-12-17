# ros_speech
音声認識・音声合成用ROSノード

## インストール
```
cd ~/catkin_ws/src
git clone https://github.com/naka-lab/ros_speech.git
cd ros_speech/
sudo ./setup.sh
```

## 実行
以下のコマンドで音声認識と音声合成のノードが立ち上がります．

```
roslaunch speech speech_node.launch 
```

## 使い方
https://github.com/naka-lab/ros_speech/blob/master/speech/node/muno.py

### 音声認識辞書の送信
サービスで認識する文字列を送信します．

```
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

rospy.wait_for_service('julius/set_grammar')
set_grammar = rospy.ServiceProxy('julius/set_grammar', SetGrammar)
set_grammar( gram, [] )
```

`[GRAMMAR]`に音声認識文法を記述します．`hello : ろぼっと、こんにちわ`の`hello`は認識文のIDを，`ろぼっと、こんにちわ`が認識される文字列を表しています．
`$noun_obj`は単語が入るスロットを表しており，`[NOUN]`以下がスロットに入る単語を定義しています．
`obj1 : ぬいぐるみ`の`obj1`が単語のIDを，`ぬいぐるみ`が認識される文字列を表しています．




### 認識結果の取得
音声が認識されると，メッセージで認識結果が送られてきます．

```
rostopic echo /julius/recogres/small_vocab 
```

メッセージには以下の情報が入っています．

- string[] sentences: 認識文の文字列のn-best
- string sentence_id: 認識文のID（スコアがトップのもの）
- string[] noun_id: スロットに入った単語のID
- string[] noun_str: スロットに入った単語の文字列

Pythonでの利用法は，[サンプル](https://github.com/naka-lab/ros_speech/blob/master/speech/node/muno.py)を参照してください．

### 音声合成
発話させる場合は，文字列をメッセージで送信します．

```
rostopic pub -1 /jtalk/sentence std_msgs/String -- "こんにちは"
```
Pythonでの利用法は，[サンプル](https://github.com/naka-lab/ros_speech/blob/master/speech/node/muno.py)を参照してください．
