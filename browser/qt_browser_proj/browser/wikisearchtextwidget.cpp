#include <QTextEdit>
#include <QScrollArea>

#include "wikisearchtextwidget.h"
#include "./wikipagesearchtext.h"

WikiSearchTextWidget::WikiSearchTextWidget(QWidget *parent, QString text)
    : QMainWindow{parent}
{
    t = new WikiPageSearchText(parent = this, text);

    this->move(100, 400);

    auto width = t->width();
    auto height = t->height();

    this->setMinimumSize(width, height);
    this->setMaximumSize(width, height);
}
