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
    void paint_(bool init);
private:
    std::vector<std::string> searchTokens;
    std::string wurl;

    const int SPACING = 20;
signals:
};

#endif // WIKIPAGELINKS_H
