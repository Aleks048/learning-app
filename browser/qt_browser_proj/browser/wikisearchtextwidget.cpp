#include <QTextEdit>
#include <QScrollArea>

#include "wikisearchtextwidget.h"
#include "./wikipagesearchtext.h"

WikiSearchTextWidget::WikiSearchTextWidget(QWidget *parent, QString text)
    : QMainWindow{parent}
{
    auto t = new WikiPageSearchText(this, text);

    this->setMinimumSize(t->width(), t->height());
    this->setMaximumSize(t->width(), t->height());
}
