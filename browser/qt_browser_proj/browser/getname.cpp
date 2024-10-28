#include <QTextEdit>
#include <QApplication>

#include "getname.h"
#include "./utils.h"
#include "./mainwindow.h"

GetName::GetName(std::string wurl, std::string text):
    QMainWindow(), wurl(wurl), text(text) {
    te = new QTextEdit(this);
    te->installEventFilter(this);
    te->setFixedSize(300, 100);
    te->show();
    this->setFixedSize(300,100);
    this->setWindowTitle("Set the name of the entry");
}

bool GetName::eventFilter(QObject* o, QEvent* ev) {
    if (ev->type() == QEvent::KeyPress) {
        auto e = dynamic_cast<QKeyEvent*>(ev);

        if (e->key() == SHIFT_KEY) {
            shiftPressed = true;
            QMainWindow::keyPressEvent(e);

        }
        else if (shiftPressed && (e->key() == ENTER_KEY)) {
            for(QWidget *widget: QApplication::topLevelWidgets()) {
                if (widget->windowTitle().toStdString() == "Browser Main Window") {
                    MainWindow* mwin = static_cast<MainWindow*>(widget);
                    auto wurl = mwin->m_browser->url().toString().toStdString();

                    auto name = this->te->toPlainText().toStdString();
                    utils::sendAddSearchPageData(wurl, name, text);
                    this->close();
                    mwin->paint_(mwin->parentWidget());
                    break;
                }
            }
        }
        else {
            QMainWindow::keyPressEvent(e);
        }
    }
    else if (ev->type() == QEvent::KeyRelease) {
        auto e = dynamic_cast<QKeyEvent*>(ev);

        if (e->key() == SHIFT_KEY) {
            shiftPressed = false;
        }

        QMainWindow::keyReleaseEvent(e);
    }
    return false;
}

