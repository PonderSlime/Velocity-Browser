import os.path
import sys
from fileinput import close
from operator import index

from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLineEdit, QPushButton, \
    QTabBar, QHBoxLayout, QMenu, QFileDialog, QTextEdit, QSplitter, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt, QObject, pyqtSlot
from setuptools.package_index import htmldecode


class CustomTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTabBar(CustomTabBar(self))

    def add_new_tab_btn(self, action):
        self.tabBar().add_new_tab_btn(action)

class BrowserSettings(QObject):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.home_url = "https://google.com"

    @pyqtSlot(str)
    def setHomeUrl(self, url):
        self.home_url = url
        print(f"Home URL set to: {url}")

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
        self.splitter = QSplitter(Qt.Horizontal)

        self.tabs = CustomTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)
        main_layout.addWidget(self.tabs)
        self.source_tab_index = None  # Track the source tab index

        self.dev_tools = QWebEngineView()
        self.dev_tools.setWindowTitle("Developer Tools")

        close_btn = QPushButton("Close Inspector")
        close_btn.clicked.connect(self.close_dev_tools)
        close_btn.setStyleSheet('background-color: #FF6347; color: white; border-radius: 5px;')

        dev_tools_layout = QVBoxLayout()
        dev_tools_layout.addWidget(self.dev_tools)
        dev_tools_layout.addWidget(close_btn)
        self.dev_tools_container = QWidget()
        self.dev_tools_container.setLayout(dev_tools_layout)

        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.dev_tools_container)
        self.splitter.setSizes([1000, 0])

        main_layout.addWidget(self.splitter)
        self.dev_tools_container.setEnabled(False)
        self.dev_tools_container.hide()

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
        self.url_bar.returnPressed.connect(self.validate_and_navigate)
        toolbar.addWidget(self.url_bar)

        menu_button = QPushButton("☰")  # Menu icon
        menu = QMenu(self)

        menu_button.setMenu(menu)
        toolbar.addWidget(menu_button)

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

        self.setCursor(Qt.ArrowCursor)
        self.dev_tools.setCursor(Qt.ArrowCursor)

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

        browser = CustomWebEngineView(self, self.dev_tools)
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_urlbar)
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_home(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("https://www.google.com"))

    def validate_and_navigate(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            url = QUrl(self.url_bar.text())
            search = self.url_bar.text()
            if url.isValid() and (url.scheme() == "http" or url.scheme() == "https"):
                print("Full URL detected with scheme:", url)
                current_browser.setUrl(url)
            elif "." in search and " " not in search:
                print("Partial URL detected without scheme:", url)
                if not url.scheme():
                    url.setScheme("http")

                current_browser.setUrl(url)
            else:
                self.perform_search(search)
                print("Search query detected:", search)

    def perform_search(self, search_text=None):
        current_browser = self.tabs.currentWidget()
        if search_text is None:
            search_text = self.url_bar.text()

        search_url = f"https://duckduckgo.com/?q={search_text}"
        current_browser.setUrl(QUrl(search_url))


    def update_urlbar(self, qurl=None):
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            qurl = current_browser.url()
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index,title)

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

    def view_page_source(self):
        if self.source_tab_index is not None and self.source_tab_index < self.tabs.count():
            current_browser = self.tabs.currentWidget()
            if isinstance(current_browser, QWebEngineView):
                current_browser.page().toHtml(self.update_page_source_tab)
            self.tabs.setCurrentIndex(self.source_tab_index)
            return
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.page().toHtml(self.handle_page_source)

    def handle_page_source(self, raw_html):
        source_tab = QWidget(self)
        layout = QVBoxLayout()
        source_tab.setLayout(layout)

        text_edit = QTextEdit()
        text_edit.setPlainText(raw_html)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        self.source_tab_index = self.tabs.addTab(source_tab, "Page Source")
        self.tabs.setCurrentIndex(self.source_tab_index)

    def update_page_source_tab(self, raw_html):
        source_tab = self.tabs.widget(self.source_tab_index)
        text_edit = source_tab.findChild(QTextEdit)
        if text_edit:
            text_edit.setPlainText(raw_html)

    def open_dev_tools(self):
        self.dev_tools_container.show()
        self.dev_tools_container.setEnabled(True)
        self.splitter.setSizes([800,400])
        self.dev_tools.setCursor(Qt.ArrowCursor)
        self.setCursor(Qt.ArrowCursor)

    def close_dev_tools(self):
        self.dev_tools_container.hide()
        self.dev_tools_container.setEnabled(False)
        self.splitter.setSizes([1000, 0])

    def setCursor(self, cursor):
        # Ensure the cursor remains ArrowCursor throughout
        super().setCursor(Qt.ArrowCursor)  # Always reset to ArrowCursor
        self.dev_tools.setCursor(Qt.ArrowCursor)

class CustomWebEngineView(QWebEngineView):
    def __init__(self, browser, dev_tools):
        super().__init__()
        self.browser = browser
        self.dev_tools = dev_tools
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        #self.page().setDevToolsPage(self.dev_tools.page()) # this is the problem! For now, it is just visual, luckily!
        self.browser.setCursor(Qt.ArrowCursor)
        self.browser.dev_tools.setCursor(Qt.ArrowCursor)

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
            if action.text() == "View page source":
                action.triggered.connect(self.browser.view_page_source)
            if action.text() == "Inspect":
               action.triggered.connect(self.browser.open_dev_tools)
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