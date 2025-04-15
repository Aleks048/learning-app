#pragma once

#include "rapidjson/document.h"

#include <string>
#include <iostream>
#include <map>

namespace data {

class JSON_file {
public:
    JSON_file(const std::string filepath);
    JSON_file(const std::string filepath, 
              const std::string json_template);
    JSON_file(const JSON_file& file);
    JSON_file(JSON_file&& file);
    ~JSON_file() = default;

    JSON_file& operator=(const JSON_file& other) // copy assignment
    {
        // implemented as move-assignment from a temporary copy for brevity
        // note that this prevents potential storage reuse
        return *this = JSON_file(other);
    }
 
    JSON_file& operator=(JSON_file&& other) noexcept // move assignment
    {
        return *this;
    }

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
    static void createFromTemplate(std::string path, 
                                   std::string json_template);
    data::JSON_file& readFile(const std::string filePath);
    // void writeFile(std::string_view filePath,);// what is the data that we bring?
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