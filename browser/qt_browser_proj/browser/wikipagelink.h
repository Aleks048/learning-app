#ifndef WIKIPAGELINK_H
#define WIKIPAGELINK_H

#include <QTextEdit>

class WikiPageLink : public QTextEdit
{
public:
    WikiPageLink();
    bool eventFilter(QObject *obj, QEvent *event) override;
    QString anchor;
    void setTextColor();
    void leaveEvent(QEvent *event) override;
    void enterEvent(QEnterEvent *event) override;
    void mousePressEvent(QMouseEvent *e) override;
};

#endif // WIKIPAGELINK_H
