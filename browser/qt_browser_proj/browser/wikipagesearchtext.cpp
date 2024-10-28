#include <QTextEdit>
#include <QKeyEvent>
#include <QFontMetrics>
#include <QSize>
#include <QApplication>

#include <iostream>
#include <cmath>

#include "wikipagesearchtext.h"
#include "./utils.h"
#include "./mainwindow.h"
#include "./wikipagelinks.h"

WikiPageSearchText::WikiPageSearchText(QWidget* parent, QString text): QTextEdit(parent){
    auto te = text.toStdString();
    this->setText(QString(te.c_str()));

    this->setFixedHeight(100);
    this->show();

    auto font = this->document()->defaultFont();
    auto fontMetrics = QFontMetrics(font);
    auto textSize = fontMetrics.size(0, this->toPlainText());

    auto w = std::max(textSize.width() + 10, 100);
    auto h = textSize.height() + 10;

    //ui->plainTextEdit->document()->blockCount();
    std::cout <<this->document()->blockCount() << " " << textSize.width() << " " << textSize.height() <<std::endl;

    this->setMinimumSize(w, this->height());
    this->setMaximumSize(w, this->height() + 10);
}

void WikiPageSearchText::setText(const QString& text) {
    originalText = text.toStdString();
    QTextEdit::setText(text);
}

void WikiPageSearchText::keyPressEvent(QKeyEvent* e) {
    if (e->key() == SHIFT_KEY) {
        shiftPressed = true;
        QTextEdit::keyPressEvent(e);

    }
    else if (shiftPressed && (e->key() == ENTER_KEY)) {
        for(QWidget *widget: QApplication::topLevelWidgets()) {
            if (widget->windowTitle().toStdString() == "Browser Main Window") {
                MainWindow* mwin = static_cast<MainWindow*>(widget);

                auto newString = this->toPlainText().toStdString();
                QWidget* topWidget = QApplication::topLevelAt(this->mapToGlobal(QPoint()));
                auto url = "http://localhost/" + mwin->url;
                utils::sendUpdateSearchText(url, topWidget->windowTitle().toStdString(), newString);
                topWidget->close();
                mwin->paint_(mwin->parentWidget());
                for(QWidget *widget: QApplication::topLevelWidgets()) {
                    if (widget->windowTitle().toStdString().find("link") != std::string::npos) {
                        WikiPageLinks* lwin = static_cast<WikiPageLinks*>(widget);
                        lwin->paint_(false);
                    }
                }
                break;
            }
        }
    }
    else {
        QTextEdit::keyPressEvent(e);
    }
}

void WikiPageSearchText::keyReleaseEvent(QKeyEvent* e) {
    if (e->key() == SHIFT_KEY) {
        shiftPressed = false;
    }

    QTextEdit::keyReleaseEvent(e);
}
