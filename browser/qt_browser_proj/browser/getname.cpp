#include <QTextEdit>

#include "getname.h"
#include "./utils.h"

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
            auto name = this->te->toPlainText().toStdString();
            utils::sendSearchPageData(wurl, name, text);
            this->close();
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
}

// void GetName::keyPressEvent(QKeyEvent* e) {
//     if (e->key() == SHIFT_KEY) {
//         shiftPressed = true;
//         QMainWindow::keyPressEvent(e);

//     }
//     else if (shiftPressed && (e->key() == ENTER_KEY)) {
//         auto name = this->te->toPlainText().toStdString();
//         utils::sendSearchPageData(wurl, name, text);
//     }
//     else {
//         QMainWindow::keyPressEvent(e);
//     }
// }

// void GetName::keyReleaseEvent(QKeyEvent* e) {
//     if (e->key() == SHIFT_KEY) {
//         shiftPressed = false;
//     }

//     QMainWindow::keyReleaseEvent(e);
// }
