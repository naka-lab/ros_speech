cd hts_engine_API-1.06
#./configure
#make

cd ../open_jtalk-1.05


./configure \
--with-hts-engine-header-path=/home/naka_t/デスクトップ/hts_engine_API-1.06/include \
--with-hts-engine-library-path=/home/naka_t/デスクトップ/hts_engine_API-1.06/lib \
--with-charset=utf-8

make
