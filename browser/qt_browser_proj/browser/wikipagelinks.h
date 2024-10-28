#ifndef WIKIPAGELINKS_H
#define WIKIPAGELINKS_H

#include <QMainWindow>
#include <QVBoxLayout>
#include <QGroupBox>

class WikiPageLinks : public QMainWindow
{
    Q_OBJECT
public:
    explicit WikiPageLinks(std::vector<std::string> searchTokens,
                           std::string wurl,
                           QWidget *parent = nullptr);


    QVBoxLayout* vlayout;
    QGroupBox* verticalGroupBox;
private:
    std::vector<std::string> searchTokens;
    void paint_(bool init);
    std::string wurl;

    const int SPACING = 20;
signals:
};

#endif // WIKIPAGELINKS_H
