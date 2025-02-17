#pragma once
#include <string>

namespace fileUtils{
    auto readFile(std::string_view filepath) -> std::string;
}