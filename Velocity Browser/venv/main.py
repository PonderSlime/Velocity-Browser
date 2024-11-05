import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLineEdit, QPushButton, \
    QTabBar, QHBoxLayout, QMenu, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt


class CustomTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTabBar(CustomTabBar(self))

    def add_new_tab_btn(self, action):
        self.tabBar().add_new_tab_btn(action)


class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_layout = QHBoxLayout(self)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.tab_layout)

        self.new_tab_btn = QPushButton("+", self)
        self.new_tab_btn.setFixedSize(30, 30)

        self.tab_layout.addStretch()
        self.tab_layout.addWidget(self.new_tab_btn)

    def add_new_tab_btn(self, action):
        self.new_tab_btn.clicked.connect(action)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velocity Browser")
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QVBoxLayout()
        self.tabs = CustomTabWidget()
        self.child = CustomWebEngineView(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)
        main_layout.addWidget(self.tabs)

        toolbar = QHBoxLayout()
        back_btn = QPushButton('←', self)
        back_btn.clicked.connect(self.navigate_back)
        back_btn.setFixedSize(30, 30)
        toolbar.addWidget(back_btn)

        forward_btn = QPushButton('→')
        forward_btn.clicked.connect(self.navigate_forward)
        forward_btn.setFixedSize(30, 30)
        toolbar.addWidget(forward_btn)

        reload_btn = QPushButton('⟳')
        reload_btn.clicked.connect(self.reload_page)
        reload_btn.setFixedSize(30, 30)
        toolbar.addWidget(reload_btn)

        self.tabs.add_new_tab_btn(lambda: self.add_new_tab(QUrl("https://www.google.com"), "New Tab"))

        home_action = QPushButton("🏠")
        home_action.clicked.connect(self.navigate_home)
        home_action.setFixedSize(30, 30)
        toolbar.addWidget(home_action)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        main_layout.addLayout(toolbar)
        self.add_new_tab(QUrl("https://www.google.com"), "Home")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget.setLayout(self.content_layout)
        main_layout.addWidget(self.content_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = CustomWebEngineView(self)
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_urlbar)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_home(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            url = QUrl(self.url_bar.text())
            if url.scheme() == "":
                url.setScheme("https")
            current_browser.setUrl(url)

    def update_urlbar(self, qurl=None):
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            qurl = current_browser.url()
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

    def save_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            url = current_browser.url()
            if url.isValid():
                # Ask the user where to save the file
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                           "HTML Files (*.html);;All Files (*)")
                if file_name:
                    # Ensure the file has a .html extension
                    if not file_name.endswith('.html'):
                        file_name += '.html'

                    # Here we would use the download signal instead
                    # You can now connect this method to the download requested signal
                    current_browser.page().profile().downloadRequested.connect(
                        lambda download: self.handle_download_requested(download, file_name)
                    )

    def handle_download_requested(self, download, file_name):
        # Accept the download and set the filename and format
        download.setDownloadFileName(file_name)
        download.setSavePageFormat(QWebEngineDownloadItem.CompleteHtmlSaveFormat)
        download.accept()  # Start the download

class CustomWebEngineView(QWebEngineView):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def handle_download_requested(self, download):
        # Optionally handle the download here
        download.accept()  # Accept the download

    def show_context_menu(self, position):
        # Create the default context menu
        menu = self.page().createStandardContextMenu()

        link_url = self.page().contextMenuData().linkUrl()
        for action in menu.actions():
            if link_url.isValid():
                if action.text() == "Open link in new tab":  # Specify the exact text of the item to remove
                    action.triggered.connect(lambda: self.browser.add_new_tab(link_url, "New Tab"))
                if action.text() == "Open link in new window":
                    action.triggered.connect(lambda: self.open_link_in_new_window(link_url))
            if action.text() == "Save page":
                action.triggered.connect(self.browser.save_page)
        menu.exec_(self.mapToGlobal(position))

    def open_link_in_new_window(self, url):
        new_window  = Browser()
        new_window.add_new_tab(url, "New Window")
        new_window.show()

app = QApplication(sys.argv)
with open("style.qss", "r") as f:
    _style = f.read()
    app.setStyleSheet(_style)
window = Browser()
window.show()
sys.exit(app.exec_())