
#include <variant>

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

        std::variant<float, bool, std::string> readProperty(const std::string propertyName);


    private:
        T document;
        std::string filepath;
    };

    template<typename T>
    class JSON {
    public:
        static void reloadFilesFromDisk();
        static void saveFilesToDisk();
        static void createFromTemplate(std::string path, 
                                    std::string json_template);
        static std::shared_ptr<data::JSON_file<T>&> readFile(const std::string filePath);
        
        template<typename P>
        P readProperty(const std::string jsonFilepath, 
            const std::string propertyName){
                return files[jsonFilepath]->readProperty(propertyName);
            };

        template<typename P>
        bool updateProperty(std::string_view jsonFilepath, 
                            std::string_view propertyName,
                            P newValue);

        template<typename P>
        bool createProperty(std::string_view jsonFilepath, 
                            std::string_view propertyName,
                            std::string_view parentName,
                            P newValue);
    private:
        static std::map<std::string, std::shared_ptr<data::JSON_file<T>>> files;
    };
}