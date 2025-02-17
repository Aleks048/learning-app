#include <string>
#include <fstream>

#include "utils.h"


namespace fileUtils{
auto readFile(std::string_view filepath) -> std::string {
    constexpr auto read_size = std::size_t(4096);
    auto stream = std::ifstream(filepath.data());
    stream.exceptions(std::ios_base::badbit);

    if (not stream) {
        throw std::ios_base::failure("file does not exist");
    }
    
    auto out = std::string();
    auto buf = std::string(read_size, '\0');
    while (stream.read(& buf[0], read_size)) {
        out.append(buf, 0, stream.gcount());
    }
    out.append(buf, 0, stream.gcount());
    return out;
}
}// and of namespace fileUtils