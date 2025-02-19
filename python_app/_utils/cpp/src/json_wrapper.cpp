#include "pybind11/pybind11.h"
#include "json.h"

PYBIND11_MODULE(JSON, m) {
  pybind11::class_<data::JSON>(m, "JSON")
     .def_static("reloadFilesFromDisk", 
                static_cast<void (*)()>(&data::JSON::reloadFilesFromDisk));
};

// class MemberClass : public JSONClassInterface
// {
// public:
//     virtual void someFunc() override
//     {
//         std::cout << "Hello from MemberClass" << std::endl;
//     }
// };