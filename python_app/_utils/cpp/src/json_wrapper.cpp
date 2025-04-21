#include <string>

#include "pybind11/pybind11.h"
#include "json.h"

PYBIND11_MODULE(JSON, m) {
  pybind11::class_<data::JSON>(m, "JSON")
     .def_static("reloadFilesFromDisk",&data::JSON::reloadFilesFromDisk)
     .def_static("saveFilesToDisk", &data::JSON::saveFilesToDisk)
     .def_static("createFromTemplate", &data::JSON::createFromTemplate)
     .def_static("readFile", &data::JSON::readFile);
};

// class MemberClass : public JSONClassInterface
// {
// public:
//     virtual void someFunc() override
//     {
//         std::cout << "Hello from MemberClass" << std::endl;
//     }
// };