#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QWidget>
#include <QEvent>
#include <QObject>

#include "./htmlview.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

private:
    Ui::MainWindow* ui;

    bool eventFilter(QObject* object, QEvent *event) override;
    void handleKeyPress(QEvent* event);


    QWidget central;
    HtmlView browser;

    std::array<std::string, 10> searchHistory;

    //NOTE: the keypress code seems to be different on mac so we hardcode
    // it to catch keypress
    const size_t KEYPRESS_CODE = 51;

    //TODO: back button
    //TODO: forward button
    //widget to show all the links for the current entry

    //std::unordered_map<std::string, std::string> linksForCurrEntries;
};
#endif // MAINWINDOW_H
