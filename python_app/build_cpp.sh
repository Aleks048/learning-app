cd "/Users/ashum048/books/utils/python_app/.build"
make clean
cmake -G "Unix Makefiles" ../ -DCMAKE_OSX_ARCHITECTURES="x86_64"
make all
make install