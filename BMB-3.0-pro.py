import sys, os
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QLineEdit, QPushButton, QToolBar, QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineDownloadRequest
)

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_URL = QUrl.fromLocalFile(os.path.join(BASE_DIR, "home-page.html"))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

# ================= TAB =================
class BrowserTab(QWebEngineView):
    def __init__(self, profile):
        super().__init__()
        page = QWebEnginePage(profile, self)
        self.setPage(page)

# ================= MAIN =================
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMB 3.0 PRO")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        self.setCentralWidget(self.tabs)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        self.toolbar.addWidget(self.url_bar)

        # ===== Buttons =====
        self.add_btn("GO", self.load_url)
        self.add_btn("+ Tab", self.new_tab)
        self.add_btn("New Profile", self.new_profile)
        self.add_btn("Incognito", self.new_incognito)
        self.add_btn("Default", lambda: self.switch_profile("Default"))
        self.add_btn("Profile-1", lambda: self.switch_profile("Profile-1"))
        self.add_btn("Profile-2", lambda: self.switch_profile("Profile-2"))


        # ===== Default profile =====
        self.profile = self.create_profile("Default")
        self.new_tab()



    #switch profile
    def switch_profile(self, name):
        self.profile = self.create_profile(name)
        self.new_tab()


    # ================= PROFILES =================
    def create_profile(self, name):
        path = os.path.join(PROFILES_DIR, name)
        os.makedirs(path, exist_ok=True)

        profile = QWebEngineProfile(name, self)
        profile.setPersistentStoragePath(path)
        profile.setCachePath(path)
        profile.downloadRequested.connect(self.handle_download)
        return profile

    def new_profile(self):
        name = f"Profile-{len(os.listdir(PROFILES_DIR))}"
        self.profile = self.create_profile(name)
        self.new_tab()

    def new_incognito(self):
        profile = QWebEngineProfile(self)  # no path → incognito
        profile.downloadRequested.connect(self.handle_download)
        tab = BrowserTab(profile)
        tab.setUrl(HOME_URL)
        self.tabs.addTab(tab, "Incognito")

    # ================= TABS =================
    def new_tab(self):
        tab = BrowserTab(self.profile)
        tab.setUrl(HOME_URL)
        tab.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()))
        self.tabs.addTab(tab, "Tab")
        self.tabs.setCurrentWidget(tab)

    def load_url(self):
        url = QUrl(self.url_bar.text())
        if not url.scheme():
            url.setScheme("https")
        self.tabs.currentWidget().setUrl(url)

    # ================= DOWNLOAD =================
    def handle_download(self, download: QWebEngineDownloadRequest):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save file", download.downloadFileName()
        )
        if path:
            download.setDownloadFileName(os.path.basename(path))
            download.setPath(path)
            download.accept()

    def add_btn(self, text, func):
        btn = QPushButton(text)
        btn.clicked.connect(func)
        self.toolbar.addWidget(btn)

# ================= RUN =================
app = QApplication(sys.argv)
browser = Browser()
browser.show()
sys.exit(app.exec())
