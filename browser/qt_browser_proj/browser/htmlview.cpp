#include "htmlview.h"
#include <QWidget>

HtmlView::HtmlView(QWidget* parent):
    QWebEngineView(parent),
    m_width(800),
    m_height(1000)
{
    //setUrl(QUrl("http://localhost/wiki/A/Dual_basis"));

    setUrl(QUrl("https://google.com"));
    this->resize(m_width, m_height);
}
