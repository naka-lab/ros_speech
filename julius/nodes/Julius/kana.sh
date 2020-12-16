cd `dirname $0`
./julius -gram kana -C SmallVocab.jconf -input mic -demo -module 10001 -record ../wav -charconv sjis utf-8
exit
