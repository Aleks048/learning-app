#include <QWidget>
#include <QKeyEvent>

#include "htmlview.h"
#include "./utils.h"


HtmlView::HtmlView(QWidget* parent, const std::string url):
    QWebEngineView(parent),
    m_width(750),
    m_height(1000)
{
    setUrl(QUrl(QString::fromStdString(url)));
    this->resize(m_width, m_height);
}
