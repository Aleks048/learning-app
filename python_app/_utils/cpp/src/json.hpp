
namespace data {
    template<typename T>
    class JSON_file {
    public:
        JSON_file(const std::string filepath);
        JSON_file(const std::string filepath, 
                  const std::string json_template);
        JSON_file(const JSON_file<T>& file);
        JSON_file(JSON_file<T>&& file);
        ~JSON_file() = default;
    
        JSON_file& operator=(const JSON_file<T>& other) // copy assignment
        {
            // implemented as move-assignment from a temporary copy for brevity
            // note that this prevents potential storage reuse
            return *this = JSON_file<T>(other);
        }
     
        JSON_file<T>& operator=(JSON_file<T>&& other) noexcept // move assignment
        {
            return *this;
        }
    
        friend std::ostream& operator<<(std::ostream& os, const JSON_file<T>& dt);

        void writeToFile();
        void reload(const std::string newFilepath);
        rapidjson::Value& readProperty();


    private:
        T document;
        std::string filepath;
    };
}