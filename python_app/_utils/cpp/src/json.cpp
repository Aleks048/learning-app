#include <cstdio>

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/filewritestream.h" 

#include "json.h"
#include "utils.h"

namespace data{

data::JSON_file::JSON_file(const std::string_view filepath):
    filepath(filepath), document()
{
    std::string jsonAsString = fileUtils::readFile(filepath);
    document.Parse(jsonAsString.c_str());
}

void data::JSON_file::reload(const std::string newFilepath)
{
    filepath = newFilepath;
    std::string jsonAsString = fileUtils::readFile(newFilepath);
    document.Parse(jsonAsString.c_str());
}

void data::JSON_file::writeToFile()
{
    FILE* fp2 = std::fopen(filepath.c_str(), "w"); // non-Windows use "w" 
    char writeBuffer[65536]; 
    rapidjson::FileWriteStream os(fp2, writeBuffer, 
                       sizeof(writeBuffer)); 
    rapidjson::Writer<rapidjson::FileWriteStream> writer(os); 
    document.Accept(writer); 
    std::fclose(fp2); 
}

std::ostream& operator<<(std::ostream &os, const data::JSON_file& jf)
{
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    jf.document.Accept(writer);
    os << buffer.GetString() << std::endl;
    return os;
}


std::map<std::string, data::JSON_file> JSON::templates; 

void data::JSON::reloadFilesFromDisk()
{
    for (auto &[key, value]: JSON::templates) {
        value.reload(key);
    }
}

void data::JSON::saveFilesToDisk()
{
    // for (auto it: JSON::templates) {
    // }
}

}