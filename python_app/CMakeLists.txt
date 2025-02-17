cmake_minimum_required(VERSION 2.8.12)
set (PYBIND11_PYTHON_VERSION "3.9")

set(CMAKE_OSX_ARCHITECTURES "x86_64")

set (PYTHON_EXECUTABLE "/Users/ashum048/books/_python_local/3.9.18/bin/python3.9")
# set (CMAKE_PREFIX_PATH "/Users/ashum048/dev/c++/tests/pybind_test")

# find_package( PkgConfig )
add_subdirectory(pybind11 REQUIRED)

add_subdirectory(_utils/cpp)