#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include <iostream>

using namespace rapidjson;

#include "json_rapidJson.hpp"

int main() {
    data::JSON_file<rapidjson::Document> jf ("/Users/ashum048/books/utils/python_app/_utils/cpp/test_data/sectionInfo.json");
    // std::cout << jf.readProperty().GetObject();
    // // 1. Parse a JSON string into DOM.
    // const char* json = "{\"project\":\"rapidjson\",\"stars\":10}";
    // Document d;
    // d.Parse(json);

    // // 2. Modify it by DOM.
    // Value& s = d["stars"];
    // s.SetInt(s.GetInt() + 1);

    // // 3. Stringify the DOM
    // StringBuffer buffer;
    // Writer<StringBuffer> writer(buffer);
    // d.Accept(writer);

    // // Output {"project":"rapidjson","stars":11}
    // std::cout << buffer.GetString() << std::endl;
    return 0;
}
