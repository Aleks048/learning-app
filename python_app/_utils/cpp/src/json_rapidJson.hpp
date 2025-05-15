#pragma once

#include "rapidjson/document.h"

#include <string>
#include <iostream>
#include <map>

#include "json.hpp"

namespace data {

// class JSON {
// public:
//     static void reloadFilesFromDisk();
//     static void saveFilesToDisk();
//     static void createFromTemplate(std::string path, 
//                                    std::string json_template);
//     static data::JSON_file& readFile(const std::string filePath);
//     // template<typename T>
//     // T readProperty(std::string jsonFilepath, 
//     //                std::string propertyName);
//     // template<typename T>
//     // void updateProperty(std::string_view jsonFilepath, 
//     //                     std::string_view propertyName,
//     //                     T newValue);
//     // template<typename T>
//     // void createProperty(std::string_view jsonFilepath, 
//     //                     std::string_view propertyName,
//     //                     std::string_view parentName,
//     //                     T newValue);
// private:
//     static std::map<std::string, data::JSON_file> templates;
// };

}