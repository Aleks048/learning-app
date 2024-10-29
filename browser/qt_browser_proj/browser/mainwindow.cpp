#include "mainwindow.h"
#include "./ui_mainwindow.h"

#include <QGridLayout>
#include <QWidget>
#include <QtCore>
#include <QEvent>
#include <QMouseEvent>
#include <QKeyEvent>
#include <QObject>
#include <QApplication>
#include <QVBoxLayout>
#include <QGroupBox>

#include "./htmlview.h"
#include "./utils.h"
#include "./textlabellink.h"
#include "./wikipagelinks.h"
#include "./getname.h"

#include <iostream>
#include <regex>

MainWindow::MainWindow(QWidget *parent,
                       std::string url)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , url(url)
    , m_wikiPageLinks()
    , horizontalGroupBox(nullptr)
{

    ui->setupUi(this);

    this->setWindowTitle(QString("Browser Main Window"));

    m_central = new QWidget();
    m_browser = new HtmlView(parent = m_central, url);

    auto cGroupBox = new QGroupBox(tr("Central layout"));
    QHBoxLayout *clayout = new QHBoxLayout;

    clayout->addWidget(m_central);
    cGroupBox->setLayout(clayout);


    QWidget* scrollAreaContent = new QWidget(parent = this);
    QVBoxLayout* mainLayout = new QVBoxLayout;

    scrollAreaContent->setLayout(mainLayout);
    mainLayout->setParent(this);

    paint_(parent, true);

    mainLayout->addWidget(horizontalGroupBox);
    mainLayout->addWidget(cGroupBox);
}

void MainWindow::paint_(QWidget* parent, bool init) {
    if (init) {
        horizontalGroupBox = new QGroupBox(tr("Wiki links"));

        hlayout = new QHBoxLayout;
        horizontalGroupBox->setLayout(hlayout);
        horizontalGroupBox->setMaximumHeight(100);
    }
    else {
        while (hlayout->count() != 0)
        {
            QLayoutItem* item = hlayout->takeAt( 0 );
            Q_ASSERT( ! item->layout() ); // otherwise the layout will leak
            delete item->widget();
            delete item;
        }
    }

    size_t tw = 0, th = 0;
    entriesData = utils::getCurrData();

    int id = 0;

    for (const auto it: entriesData) {
        const auto v = it.second;
        std::string k = it.first;

        auto urlCall = [k, v](QEvent *ev, TextLabelLink* self) {
            MainWindow* mwin;
            for(QWidget *widget: QApplication::topLevelWidgets()) {
                if (widget->windowTitle().toStdString() == "Browser Main Window") {
                    mwin = static_cast<MainWindow*>(widget);
                    break;
                }
            }

            if (ev->type() == QEvent::MouseButtonPress) {
                auto* e = dynamic_cast<QMouseEvent*>(ev);
                std::string key = std::regex_replace(k, std::regex("wiki"), "wiki/A");
                auto url = "http://localhost/" + key;

                mwin->url = key;
                mwin->m_browser->setUrl(QString(url.c_str()));

                for (QWidget* widget: QApplication::topLevelWidgets()) {
                    if (widget->windowTitle().toStdString().find("link:") != std::string::npos) {
                        widget->close();
                    }
                }

                auto win = new WikiPageLinks(v, k);
                auto title = "__link: " + key;
                win->setWindowTitle(QString(title.c_str()));
                win->setAttribute( Qt::WA_DeleteOnClose );
                win->show();
            }
            else if (ev->type() == QEvent::KeyPress) {
                auto* e = dynamic_cast<QKeyEvent*>(ev);

                if (self->cmdPressed && (e->key() == self->D_KEY)) {
                    utils::sendDeletePageEntry(mwin->url);
                    QWidget* topWidget = QApplication::topLevelAt(self->mapToGlobal(QPoint()));
                    auto mWin = dynamic_cast<MainWindow*>(topWidget);
                    mWin->paint_(topWidget->parentWidget());
                }
            }
        };

        auto l = new TextLabelLink(urlCall);

        l->installEventFilter(l);
        l->setText(QString(it.first.c_str()));
        hlayout->addWidget(l);

        auto font = l->document()->defaultFont();
        auto fontMetrics = QFontMetrics(font);
        auto textSize = fontMetrics.size(0, l->toPlainText());

        auto w = textSize.width() + 10;
        auto h = textSize.height() + 10;
        l->setMinimumSize(w, h);
        l->setMaximumSize(w, h);

        tw += w;
        th += h;

        ++id;
    }

    horizontalGroupBox->setMinimumSize(tw + 40, th + 40);
    horizontalGroupBox->setMaximumSize(tw + 40, th + 40);
}

void MainWindow::closeEvent(QCloseEvent *e) {
    for (QWidget* widget: QApplication::topLevelWidgets()) {
        widget->close();
    }
}

void MainWindow::keyPressEvent(QKeyEvent* e) {
    if (e->key() == SHIFT_KEY) {
        shiftPressed = true;
        QMainWindow::keyPressEvent(e);

    }
    else if (shiftPressed && (e->key() == ENTER_KEY)) {
        auto searchText = this->m_browser->selectedText().toStdString();
        auto getName = new GetName(url, searchText);
        getName->show();
    }
    else {
        QMainWindow::keyPressEvent(e);
    }
}

void MainWindow::keyReleaseEvent(QKeyEvent* e) {
    if (e->key() == SHIFT_KEY) {
        shiftPressed = false;
    }

    QMainWindow::keyReleaseEvent(e);
}

void MainWindow::handleKeyPress(QEvent* event)
{
    if (dynamic_cast<QKeyEvent*>(event)->text() == QString("d")) {
        //do something for some key
        return;
    }
    else {
        // default for other keys
        return;
    }
}

MainWindow::~MainWindow()
{
    delete ui;
}
