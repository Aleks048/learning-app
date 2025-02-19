// class https://stackoverflow.com/a/59089345

#include "pybind11/pybind11.h"
#include <iostream>
#include <memory>


class Example
{
public:
    Example()
        :
        member(std::make_unique<MemberClass>())
    {}

    std::unique_ptr<MemberClassInterface> member;
};


PYBIND11_MODULE(pyexample, m)
{
    pybind11::class_<JSONClassInterface>(m, "MemberClassInterface")
        .def("someFunc", &JSNOClassInterface::someFunc);

    pybind11::class_<Example>(m, "Example")
        .def(pybind11::init())
        .def_property_readonly("member", [](Example const& e) { return e.member.get(); });
}