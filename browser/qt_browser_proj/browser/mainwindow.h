#pragma once
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QWidget>
#include <QEvent>
#include <QObject>
#include <QCloseEvent>
#include <QGroupBox>
#include <QHBoxLayout>


#include "./htmlview.h"
#include "./wikipagelink.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget* parent = nullptr,
               std::string url = "https://google.com");
    ~MainWindow();

    void paint_(QWidget* parent, bool init = false);
private:
    Ui::MainWindow* ui;
    QWidget* m_central;
    QGroupBox* horizontalGroupBox;
    QHBoxLayout* hlayout;

    //bool eventFilter(QObject* object, QEvent *event) override;
    void handleKeyPress(QEvent* event);

    void closeEvent(QCloseEvent *e) override;

    std::vector<WikiPageLink*> m_wikiPageLinks;

    //NOTE: the keypress code seems to be different on mac so we hardcode
    // it to catch keypress
    const size_t KEYPRESS_CODE = 51;

    void keyPressEvent(QKeyEvent* e) override;
    void keyReleaseEvent(QKeyEvent* e) override;

    bool shiftPressed = true;

    int SHIFT_KEY = 16777248;
    int ENTER_KEY = 16777220;

public:
    HtmlView* m_browser;

    std::string url;

    std::unordered_map<std::string, std::vector<std::string>> entriesData;

    //TODO: back button
    //TODO: forward button
    //widget to show all the links for the current entry

    //std::unordered_map<std::string, std::string> linksForCurrEntries;
};
#endif // MAINWINDOW_H
