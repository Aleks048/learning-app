#pragma once


#ifndef UTILS_H
#define UTILS_H

#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <unordered_map>

namespace utils {

std::vector<std::string> splitString(std::string& s, const std::string& delimiter);

std::unordered_map<std::string, std::vector<std::string>> getCurrData();

void sendSearchTextData(std::string name, std::string searchText);

void sendSearchNameData(std::string name);

void sendDeleteSearchEntry(std::string wurl, std::string name);

void sendDeletePageEntry(std::string wurl);

void sendSearchPageData(std::string wurl, std::string name, std::string text);

} //end of utils


#endif // UTILS_H
