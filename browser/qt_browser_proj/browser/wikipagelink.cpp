#include "wikipagelink.h"
#include <QCursor>
#include <QEvent>
#include <QMouseEvent>
#include <QMainWindow>
#include <QApplication>

#include <iostream>

#include "./wikipagelinks.h"
#include "./mainwindow.h"

WikiPageLink::WikiPageLink() {
    insertPlainText(QString("test text"));
    setReadOnly(true);
    this->resize(1000, 100);
    //connect(this, SIGNAL(textChanged()), this, SLOT(setTextColor()));
}

bool WikiPageLink::eventFilter(QObject *obj, QEvent *event) {
    if (event->type() == QEvent::MouseMove)
    {
        //QMouseEvent* mouseEvent = dynamic_cast<QMouseEvent*>(event);

        //statusBar()->showMessage(QString("Mouse move (%1,%2)").arg(mouseEvent->pos().x()).arg(mouseEvent->pos().y()));
    }
    return false;
}

void WikiPageLink::mousePressEvent(QMouseEvent *e) {
    MainWindow* mwin = static_cast<MainWindow*>(QApplication::activeWindow());
    auto entries = mwin->entriesData;

    std::string k = toPlainText().toStdString();

    auto v = entries[k];

    auto win = new WikiPageLinks(v, k);
    win->setAttribute( Qt::WA_DeleteOnClose );
    win->show();
    //deleteLater();
}

void WikiPageLink::leaveEvent(QEvent *event) {
    QTextEdit::setTextColor(QColor(255, 255, 255));
    this->setText(this->toPlainText());
}

void WikiPageLink::enterEvent(QEnterEvent *event) {
    QTextEdit::setTextColor(QColor(0, 0, 255));
    this->setText(this->toPlainText());
}
