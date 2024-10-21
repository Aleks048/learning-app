#ifndef UTILS_H
#define UTILS_H

#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <array>

namespace {
std::string executeCmdAndGetResults(const char* cmd) {
    // comes from https://stackoverflow.com/a/478960
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);

    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}
std::vector<std::string> splitString(std::string& s, const std::string& delimiter) {
    std::vector<std::string> tokens;
    size_t pos = 0;
    std::string token;

    while ((pos = s.find(delimiter)) != std::string::npos) {
        token = s.substr(0, pos);
        tokens.push_back(token);
        s.erase(0, pos + delimiter.length());
    }
    tokens.push_back(s);

    return tokens;
}
}

std::unordered_map<std::string, std::vector<std::string>> getCurrData() {
    auto result = executeCmdAndGetResults("/Users/ashum048/books/utils/browser/qt_browser_proj/browser/urlScript.sh KIK://test/1/2/3/4");

    std::vector<std::string> entries = splitString(result, "\n");


    std::unordered_map<std::string, std::vector<std::string>> out;

    for (auto s: entries) {
        std::vector<std::string> keyAndValues = splitString(s, "::::");
        auto key = keyAndValues.back();
        keyAndValues.pop_back();
        out[key] = keyAndValues;
    }

    return out;
}


#endif // UTILS_H
