#include <QObject>
#include <QCursor>
#include <QEvent>
#include <QMouseEvent>
#include <QKeyEvent>
#include <QApplication>


#include <iostream>

#include "textlabellink.h"
#include "./utils.h"

TextLabelLink::TextLabelLink(std::function<void(QEvent *e, TextLabelLink* self)> urlCall):
    urlCall(urlCall) {
    this->setReadOnly(true);
}

void TextLabelLink::keyPressEvent(QKeyEvent* e) {
    std::cout << e->key() << std::endl;
    if (e->key() == SHIFT_KEY) {
        shiftPressed = true;
        QTextEdit::keyPressEvent(e);

    }
    else if (e->key() == CMD_KEY) {
        cmdPressed = true;
        QTextEdit::keyPressEvent(e);

    }
    else if (shiftPressed && (e->key() == ENTER_KEY)) {
        auto newString = this->toPlainText().toStdString();
        utils::sendSearchNameData(newString);
    }
    else if (cmdPressed && (e->key() == D_KEY)) {
        urlCall(static_cast<QEvent*>(e), this);
    }
    else {
        QTextEdit::keyPressEvent(e);
    }
}

void TextLabelLink::keyReleaseEvent(QKeyEvent* e) {
    if (e->key() == SHIFT_KEY) {
        shiftPressed = false;
    }
    else if (e->key() == CMD_KEY) {
        cmdPressed = false;
    }

    QTextEdit::keyReleaseEvent(e);
}

void TextLabelLink::mousePressEvent(QMouseEvent* e) {
    urlCall(static_cast<QEvent*>(e), this);
    QTextEdit::mousePressEvent(e);
}

void TextLabelLink::leaveEvent(QEvent *e) {
    QTextEdit::setTextColor(QColor(255, 255, 255));
    this->setText(this->toPlainText());

    QTextEdit::leaveEvent(e);
}

void TextLabelLink::enterEvent(QEnterEvent *e) {
    QWidget* topWidget = QApplication::topLevelAt(this->mapToGlobal(QPoint()));
    topWidget->activateWindow();

    this->setFocus();

    QTextEdit::setTextColor(QColor(0, 0, 255));
    this->setText(this->toPlainText());

    QTextEdit::enterEvent(e);
}
