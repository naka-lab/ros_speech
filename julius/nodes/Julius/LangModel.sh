cd `dirname $0`
./juliusExe-4.3.1 -C LangModel.jconf -d $1 -v $2 -module 10003 -charconv sjis utf-8
exit
