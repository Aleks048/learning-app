#ifndef GETNAME_H
#define GETNAME_H

#include <QMainWindow>
#include <QTextEdit>
#include <QKeyEvent>
#include <QEvent>
#include <QObject>

#include <iostream>

class GetName : public QMainWindow
{
    Q_OBJECT
public:
    explicit GetName(std::string wurl, std::string text);

private:
    // void keyPressEvent(QKeyEvent* e) override;
    // void keyReleaseEvent(QKeyEvent* e) override;
    bool eventFilter(QObject* o, QEvent* ev) override;

    std::string wurl;
    std::string text;
    QTextEdit* te;

    bool shiftPressed = false;

    int SHIFT_KEY = 16777248;
    int ENTER_KEY = 16777220;
signals:
};


#endif // GETNAME_H
