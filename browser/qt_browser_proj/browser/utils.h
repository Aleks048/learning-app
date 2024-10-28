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

void sendUpdateSearchText(std::string wurl, std::string name, std::string newSearchText);

void sendUpdateLinkName(std::string wurl, std::string newName, std::string oldName);

void sendDeleteSearchEntry(std::string wurl, std::string name);

void sendDeletePageEntry(std::string wurl);

void sendAddSearchPageData(std::string wurl, std::string name, std::string text);

} //end of utils


#endif // UTILS_H
