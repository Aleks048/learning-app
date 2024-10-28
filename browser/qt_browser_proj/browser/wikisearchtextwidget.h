#ifndef WIKISEARCHTEXTWIDGET_H
#define WIKISEARCHTEXTWIDGET_H

#include <QMainWindow>
#include <QString>
#include <QKeyEvent>

class WikiSearchTextWidget : public QMainWindow
{
    Q_OBJECT
public:
    explicit WikiSearchTextWidget(QWidget *parent, QString text);
signals:
};

#endif // WIKISEARCHTEXTWIDGET_H
