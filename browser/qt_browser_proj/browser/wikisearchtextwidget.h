#ifndef WIKISEARCHTEXTWIDGET_H
#define WIKISEARCHTEXTWIDGET_H

#include <QMainWindow>
#include <QString>
#include <QKeyEvent>

#include "./wikipagesearchtext.h"

class WikiSearchTextWidget : public QMainWindow
{
    Q_OBJECT
public:
    explicit WikiSearchTextWidget(QWidget *parent, QString text);
private:
    WikiPageSearchText* t;
signals:
};

#endif // WIKISEARCHTEXTWIDGET_H
