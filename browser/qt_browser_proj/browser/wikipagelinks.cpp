#include <QGroupBox>
#include <QVBoxLayout>
#include <QTextEdit>
#include <QMouseEvent>
#include <QApplication>

#include <iostream>

#include "wikipagelinks.h"
#include "./textlabellink.h"
#include "./mainwindow.h"
#include "./utils.h"
#include "./wikisearchtextwidget.h"


WikiPageLinks::WikiPageLinks(std::vector<std::string> searchTokens,
                             std::string wurl,
                             QWidget *parent)
    : QMainWindow{parent}
    , searchTokens(searchTokens)
    , wurl(wurl)
{
    verticalGroupBox = new QGroupBox(tr("Wiki links"), parent = this);
    vlayout = new QVBoxLayout;

    vlayout->setSpacing(SPACING);
    verticalGroupBox->setLayout(vlayout);
    verticalGroupBox->setMinimumHeight(500);
    paint_(true);
}

void WikiPageLinks::paint_(bool init) {
    if (!init){
        while (vlayout->count() != 0)
        {
            QLayoutItem* item = vlayout->takeAt( 0 );
            Q_ASSERT( ! item->layout() ); // otherwise the layout will leak
            delete item->widget();
            delete item;
        }

        auto entriesData = utils::getCurrData();

        searchTokens = entriesData[wurl];
    }

    size_t tw = 0, th = 0;

    for (auto textAndValue: searchTokens) {
        std::vector<std::string> split = utils::splitString(textAndValue, "////");

        auto text = split[0];
        auto searchText = split[1];

        auto urlCall = [text, searchText](QEvent *ev, TextLabelLink* self){
            if (ev->type() == QEvent::MouseButtonPress) {
                auto* e = dynamic_cast<QMouseEvent*>(ev);
                if (e->button() == Qt::LeftButton) {
                    if (self->cmdPressed) {
                        if (self->shiftPressed) {
                            auto t = new WikiSearchTextWidget(self, QString(searchText.c_str()));
                            t->setWindowTitle(QString(text.c_str()));
                            t->setAttribute( Qt::WA_DeleteOnClose );
                            t->show();
                        }
                        else {
                            self->setReadOnly(false);
                        }
                        return;
                    }

                    self->setReadOnly(true);

                    for(QWidget *widget: QApplication::topLevelWidgets()) {
                        if (widget->windowTitle().toStdString() == "Browser Main Window") {
                            MainWindow* mwin = static_cast<MainWindow*>(widget);
                            auto browser = mwin->m_browser;
                            browser->findText(QString(searchText.c_str()));
                        }
                    }
                }
                else if ((e->button() == Qt::MiddleButton)) {
                    if (self->shiftPressed) {
                        auto t = new WikiSearchTextWidget(self, QString(searchText.c_str()));
                        t->setWindowTitle(QString(text.c_str()));
                        t->setAttribute( Qt::WA_DeleteOnClose );
                        t->show();
                    }
                    else {
                        self->setReadOnly(false);
                    }
                }
            }
            else if (ev->type() == QEvent::KeyPress) {
                auto* e = dynamic_cast<QKeyEvent*>(ev);

                if (self->cmdPressed && (e->key() == self->D_KEY)) {
                    for(QWidget *widget: QApplication::topLevelWidgets()) {
                        if (widget->windowTitle().toStdString() == "Browser Main Window") {
                            MainWindow* mwin = static_cast<MainWindow*>(widget);

                            auto wurl = "http://localhost/" + mwin->url;

                            utils::sendDeleteSearchEntry(wurl,
                                                         self->toPlainText().toStdString());
                            QWidget* topWidget = QApplication::topLevelAt(self->mapToGlobal(QPoint()));
                            auto mWin = dynamic_cast<WikiPageLinks*>(topWidget);
                            mWin->paint_(false);
                            break;
                        }
                    }

                }
            }
        };

        auto l = new TextLabelLink(urlCall);

        l->setText(QString(text.c_str()));
        vlayout->addWidget(l);

        auto font = l->document()->defaultFont();
        auto fontMetrics = QFontMetrics(font);
        auto textSize = fontMetrics.size(0, l->toPlainText());

        auto w = textSize.width() + 10;
        auto h = textSize.height() + 10;
        l->setMinimumSize(w + 10, h + 10);
        l->setMaximumSize(w + 10, h + 10);

        tw += w;
        th += h + SPACING;
    }

    verticalGroupBox->setMinimumSize(tw + 40, th + 20);
    verticalGroupBox->setMaximumSize(tw + 40, th + 20);

    this->setGeometry(QRect(100, 100, tw + 40, th + 20));
}
