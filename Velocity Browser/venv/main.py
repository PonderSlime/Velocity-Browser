import sys
from PyQt5.QtCore import *
from PyQt5.QtCore import QUrlQuery
from  PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Velocity Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()
        self.tabs = QTabWidget()

        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        # nav bar
        self.navbar = QToolBar("Navigation")
        self.addToolBar(self.navbar)

        new_tab_action = QAction('New Tab', self)
        new_tab_action.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_action)

        # Add an initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "Home")

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        self.navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        self.navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        self.navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)

    def navigate_home(self):
        self.browser.setUrl(QUrl('https://google.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())
    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl('https://google.com')
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(1)
    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
app = QApplication(sys.argv)
QApplication.setApplicationName('Velocity Browser')
window = MainWindow()
app.exec_()