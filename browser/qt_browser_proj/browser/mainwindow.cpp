#include "mainwindow.h"
#include "./ui_mainwindow.h"

#include <QGridLayout>
#include <QWidget>
#include <QtCore>
#include <QEvent>
#include <QKeyEvent>
#include <QObject>
#include <QApplication>

#include "./htmlview.h"
#include "./utils.h"

#include <iostream>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , central(parent = this)
    , browser(parent = &central)
{
    ui->setupUi(this);
    browser.installEventFilter(this);

    this->setCentralWidget(&central);

    QGridLayout layout = QGridLayout(parent = &central);
    layout.addWidget(&browser);
    QWidget another(&central);
    layout.addWidget(&another);
    another.setFocusPolicy(Qt::StrongFocus);
}

bool MainWindow::eventFilter(QObject *object, QEvent *event)
{
    if ((event->type() == KEYPRESS_CODE))
    {
        this->handleKeyPress(event);
        return false;
    }
    return QMainWindow::eventFilter(object, event);
}

void MainWindow::handleKeyPress(QEvent* event)
{
    if (dynamic_cast<QKeyEvent*>(event)->text() == QString("d")) {
        getCurrData();
        //do somethin for some key
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
