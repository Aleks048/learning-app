#pragma once

#include "rapidjson/document.h"

#include <string>
#include <iostream>
#include <map>

namespace data {

class JSON_file {
public:
    JSON_file(const std::string_view filepath);

    friend std::ostream& operator<<(std::ostream& os, const JSON_file& dt);
    void writeToFile();
    void reload(const std::string newFilepath);
private:
    rapidjson::Document document;
    std::string filepath;
};

class JSON {
public:
    static void reloadFilesFromDisk();
    static void saveFilesToDisk();
    // void readFile(std::string_view filePath);
    // // void writeFile(std::string_view filePath);// what is the data that we bring?
    // void readProperty(std::string_view jsonFilepath, 
    //                   std::string_view propertyName);
    // template<typename T>
    // void updateProperty(std::string_view jsonFilepath, 
    //                     std::string_view propertyName,
    //                     T newValue);
    // template<typename T>
    // void createProperty(std::string_view jsonFilepath, 
    //                     std::string_view propertyName,
    //                     std::string_view parentName,
    //                     T newValue);
private:
    static std::map<std::string, data::JSON_file> templates;
};

}