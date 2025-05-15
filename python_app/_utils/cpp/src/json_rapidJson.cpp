#include <cstdio>

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/filewritestream.h" 

#include "utils.h"

#include "json_rapidJson.hpp"

namespace data {

template<>
rapidjson::Value& data::JSON_file<rapidjson::Document>::readProperty() {
    return document["_tocData"];
};

template<>
data::JSON_file<rapidjson::Document>::JSON_file(const std::string filepath):
filepath(filepath), document()
{
    std::string jsonAsString = fileUtils::readFile(filepath);
    document.Parse(jsonAsString.c_str());
}

template<>
data::JSON_file<rapidjson::Document>::JSON_file(const std::string filepath,
    const std::string json_template):
filepath(filepath), document()
{
    document.Parse(json_template.c_str());
}
    
template<>
data::JSON_file<rapidjson::Document>::JSON_file(const JSON_file& file):
    filepath(file.filepath), document()
{
    std::string jsonAsString = fileUtils::readFile(filepath);
    document.Parse(jsonAsString.c_str());
}

template<>
data::JSON_file<rapidjson::Document>::JSON_file(JSON_file&& file):
    filepath(file.filepath), document()
{
    std::string jsonAsString = fileUtils::readFile(filepath);
    document.Parse(jsonAsString.c_str());
}

template<>
void data::JSON_file<rapidjson::Document>::reload(const std::string newFilepath)
{
    filepath = newFilepath;
    std::string jsonAsString = fileUtils::readFile(newFilepath);
    document.Parse(jsonAsString.c_str());
}

template<>
void data::JSON_file<rapidjson::Document>::writeToFile()
{
    FILE* fp2 = std::fopen(filepath.c_str(), "w"); // non-Windows use "w" 
    char writeBuffer[65536]; 
    rapidjson::FileWriteStream os(fp2, writeBuffer, 
                       sizeof(writeBuffer)); 
    rapidjson::Writer<rapidjson::FileWriteStream> writer(os); 
    document.Accept(writer); 
    std::fclose(fp2); 
}

std::ostream& operator<<(std::ostream &os, const data::JSON_file<rapidjson::Document>& jf)
{
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    jf.document.Accept(writer);
    os << buffer.GetString() << std::endl;
    return os;
}




// std::map<std::string, data::JSON_file> data::JSON::templates; 

// void data::JSON::reloadFilesFromDisk()
// {
//     for (auto &[key, value]: JSON::templates) {
//         value.reload(key);
//     }
// }

// void data::JSON::saveFilesToDisk()
// {
//     for (auto &[key, value]: JSON::templates) {
//         value.writeToFile();
//     }
// }

// void data::JSON::createFromTemplate(const std::string path, 
//                                     const std::string json_template)
// {
//     data::JSON_file file(path, json_template);
//     file.writeToFile();
// }

// data::JSON_file& data::JSON::readFile(const std::string filePath)
// {
//     if (JSON::templates.find(filePath) != JSON::templates.end()) {
//         data::JSON_file jf {filePath};
//         auto p = std::make_pair(filePath, jf);
//         //TODO: not ideal should change later to use the [] operator
//         data::JSON::templates.insert(p);
//     }

//     return data::JSON::templates.at(filePath);
// }

}