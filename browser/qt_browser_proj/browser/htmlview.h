#ifndef HTMLVIEW_H
#define HTMLVIEW_H

#include <QWebEngineView>
#include <QWidget>

class HtmlView : public QWebEngineView
{
public:
    HtmlView(QWidget* parent, const std::string url);
private:
    size_t m_width;
    size_t m_height;
};

#endif // HTMLVIEW_H
