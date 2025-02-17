# project(pybind11_json)
# pybind11_add_module(pybind11_json 
#     wrapper.cpp 
#     json.cpp)
# set_target_properties(pybind11_json PROPERTIES LINKER_LANGUAGE CXX)
# install(TARGETS pybind11_json DESTINATION "/Users/ashum048/books/utils/python_app/_utils/cpp")

project(test)

add_executable(test src/main.cpp src/json.cpp src/utils.cpp)
set_target_properties(test PROPERTIES LINKER_LANGUAGE CXX CXX_STANDARD 17)

target_include_directories(test PUBLIC "/Users/ashum048/books/utils/python_app/_utils/cpp/.deps/rapidjson/include")
install(TARGETS test DESTINATION "/Users/ashum048/books/utils/python_app/_utils/cpp/.bin")