#include "rapidjson/document.h"

#include <string>
#include <iostream>

class JSON_file {
public:
    JSON_file(std::string_view filepath);

    friend std::ostream& operator<<(std::ostream& os, const JSON_file& dt);
private:
    rapidjson::Document document;
    std::string_view filepath;
};