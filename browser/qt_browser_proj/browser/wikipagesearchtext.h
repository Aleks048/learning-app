#ifndef WIKIPAGESEARCHTEXT_H
#define WIKIPAGESEARCHTEXT_H

#include <QTextEdit>

class WikiPageSearchText : public QTextEdit
{
public:
    WikiPageSearchText(QWidget* parent, QString text);

    void setText(const QString& text);

    void keyPressEvent(QKeyEvent* e) override;
    void keyReleaseEvent(QKeyEvent* e) override;

    bool shiftPressed = false;

    int SHIFT_KEY = 16777248;
    int ENTER_KEY = 16777220;
private:
    std::string originalText;
};

#endif // WIKIPAGESEARCHTEXT_H
