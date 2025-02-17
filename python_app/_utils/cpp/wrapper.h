// class https://stackoverflow.com/a/59089345

// pybind11_wrapper.cpp
#include <pybind11/pybind11.h>

float mult(int i, int j){return i * j;};

PYBIND11_MODULE(pybind11_example, m) {
    m.doc() = "pybind11 example plugin"; // Optional module docstring
    m.def("cpp_function", &mult, "A function that multiplies two numbers");
}