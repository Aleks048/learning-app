#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#include "json.h"
#include "utils.h"

JSON_file::JSON_file(std::string_view filepath):
    filepath(filepath), document()
{
    std::string jsonAsString = fileUtils::readFile(filepath);
    document.Parse(jsonAsString.c_str());
}

std::ostream& operator<<(std::ostream &os, const JSON_file& jf){
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    jf.document.Accept(writer);
    os << buffer.GetString() << std::endl;
    return os;
}