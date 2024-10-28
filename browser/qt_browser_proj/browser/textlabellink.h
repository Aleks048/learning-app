#ifndef TEXTLABELLINK_H
#define TEXTLABELLINK_H

#include <QTextEdit>
#include <QKeyEvent>
#include <QEvent>

class TextLabelLink : public QTextEdit
{
public:
    TextLabelLink(std::function<void(QEvent *e, TextLabelLink* self)> urlCall);
    //bool eventFilter(QObject *obj, QEvent *event) override;
    void setText(const QString& text);
    void leaveEvent(QEvent *event) override;
    void enterEvent(QEnterEvent *event) override;
    void mousePressEvent(QMouseEvent *e) override;
    void keyPressEvent(QKeyEvent* e) override;
    void keyReleaseEvent(QKeyEvent* e) override;

    // bool eventFilter(QObject *, QEvent *) override;

    std::function<void(QEvent *e, TextLabelLink* self)> urlCall;

    bool shiftPressed = false;
    bool cmdPressed = false;

    const int SHIFT_KEY = 16777248;
    const int ENTER_KEY = 16777220;
    const int CMD_KEY = 16777249;
    const int D_KEY = 68;

private:
    std::string originalText;
};

#endif // TEXTLABELLINK_H
