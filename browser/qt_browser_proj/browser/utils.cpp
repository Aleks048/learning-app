#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <unordered_map>

#include "./utils.h"


namespace {

const std::string URL_SCRIPT_PATH = "/Users/ashum048/books/utils/browser/qt_browser_proj/browser/urlScript.sh";

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
}


namespace utils {

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

std::unordered_map<std::string, std::vector<std::string>> getCurrData() {
    std::string url = URL_SCRIPT_PATH + " KIK://get";
    auto result = executeCmdAndGetResults(url.c_str());

    std::vector<std::string> entries = splitString(result, "\n");
    entries.erase(entries.end() - 1);

    std::unordered_map<std::string, std::vector<std::string>> out;

    for (auto s: entries) {
        std::cout << "e:" << s << std::endl;
        std::vector<std::string> keyAndValues = splitString(s, "::::");
        auto key = keyAndValues.back();
        keyAndValues.pop_back();
        out[key] = keyAndValues;
    }

    return out;
}

void sendSearchTextData(std::string name, std::string searchText) {
    std::string url = URL_SCRIPT_PATH + " 'KIK://searchText/" + name + "/" + searchText + "'";
    executeCmdAndGetResults(url.c_str());
}

void sendSearchNameData(std::string name) {
    std::string url = URL_SCRIPT_PATH + " 'KIK://searchName/" + name + "'";
    executeCmdAndGetResults(url.c_str());
}


void sendDeleteSearchEntry(std::string wurl, std::string name) {
    std::string url = URL_SCRIPT_PATH + " 'KIK://deleteName/" + wurl
                      + "/" + name + "'";
    executeCmdAndGetResults(url.c_str());
};

void sendDeletePageEntry(std::string wurl) {
    std::string url = URL_SCRIPT_PATH + " 'KIK://deletePage/" + wurl + "'";
    executeCmdAndGetResults(url.c_str());
};

void sendSearchPageData(std::string wurl, std::string name, std::string text) {
    std::string url = URL_SCRIPT_PATH + " 'KIK://searchPage/" + wurl
                      + "/" + name + "/" + text + "'";
    executeCmdAndGetResults(url.c_str());
}
}
