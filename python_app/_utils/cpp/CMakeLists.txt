if (CMAKE_BUILD_TYPE STREQUAL "Release")
    project(JSON)
    pybind11_add_module(JSON 
        src/json_wrapper.cpp 
        src/json_rapidJson.cpp
        src/utils.cpp)
    set_target_properties(JSON PROPERTIES LINKER_LANGUAGE CXX CXX_STANDARD 17)

    target_include_directories(JSON PUBLIC "/Users/ashum048/books/utils/python_app/_utils/cpp/.deps/rapidjson/include")

    install(TARGETS JSON DESTINATION "/Users/ashum048/books/utils/python_app/_utils/cpp")
else()
    project(test)

    add_executable(test 
        src/main.cpp 
        src/json_rapidJson.cpp 
        src/utils.cpp)
    set_target_properties(test PROPERTIES LINKER_LANGUAGE CXX CXX_STANDARD 17)

    target_include_directories(test PUBLIC "/Users/ashum048/books/utils/python_app/_utils/cpp/.deps/rapidjson/include")
    install(TARGETS test DESTINATION "/Users/ashum048/books/utils/python_app/_utils/cpp/.bin")
endif()