import sys
import threading
from pathlib import Path
from urllib.parse import quote_plus, urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWebEngineCore import (
    QWebEngineDownloadRequest,
    QWebEnginePage,
    QWebEngineProfile,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QStatusBar,
    QTabWidget,
    QToolBar,
)

from quantum_app.app import create_server


HOME_URL = "https://www.google.com/"


def address_to_url(address: str) -> str:
    value = address.strip()
    if not value:
        return HOME_URL

    parsed = urlparse(value)
    if parsed.scheme in {"http", "https", "file"}:
        return value
    if value.startswith("localhost"):
        return f"http://{value}"
    if " " not in value and "." in value:
        return f"https://{value}"
    return f"https://www.google.com/search?q={quote_plus(value)}"


class BrowserPage(QWebEnginePage):
    def __init__(self, browser: "BrowserWindow", parent=None):
        super().__init__(parent)
        self.browser = browser

    def createWindow(self, window_type):
        return self.browser.add_tab(switch=True).page()


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiverse Browser")
        self.resize(1280, 820)
        self.quantum_server = create_server()
        self.quantum_thread = threading.Thread(
            target=self.quantum_server.serve_forever,
            name="multiverse-quantum-engine",
            daemon=True,
        )
        self.quantum_thread.start()

        self.tabs = QTabWidget(tabsClosable=True, movable=True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_current_tab)
        self.setCentralWidget(self.tabs)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("URL または検索語句を入力")
        self.address_bar.returnPressed.connect(self.navigate)

        self.progress = QProgressBar()
        self.progress.setMaximumWidth(140)
        self.progress.setTextVisible(False)
        self.progress.hide()

        self._create_toolbar()
        self._create_status_bar()
        self._configure_downloads()
        self.add_tab(QUrl(HOME_URL), switch=True)

    def _create_toolbar(self):
        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self._action("←", "戻る", QKeySequence.Back, self.go_back))
        toolbar.addAction(self._action("→", "進む", QKeySequence.Forward, self.go_forward))
        toolbar.addAction(self._action("↻", "再読み込み", QKeySequence.Refresh, self.reload))
        toolbar.addAction(self._action("⌂", "ホーム", None, self.go_home))
        toolbar.addSeparator()
        toolbar.addWidget(self.address_bar)
        toolbar.addAction(
            self._action("⚛²", "量子ツインエンジン", None, self.open_quantum_engine)
        )
        toolbar.addAction(
            self._action("QAI", "量子AI創薬シミュレーター", None, self.open_drug_discovery)
        )
        toolbar.addAction(self._action("+", "新しいタブ", QKeySequence.AddTab, self.new_tab))

    def _create_status_bar(self):
        status = QStatusBar()
        status.addPermanentWidget(self.progress)
        self.setStatusBar(status)

    def _configure_downloads(self):
        self.tabs.currentChanged.connect(lambda _: self.statusBar().clearMessage())
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

    def _action(self, text, tooltip, shortcut, callback):
        action = QAction(text, self)
        action.setToolTip(tooltip)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        return action

    def current_view(self):
        return self.tabs.currentWidget()

    def add_tab(self, url=None, switch=False):
        view = QWebEngineView()
        view.setPage(BrowserPage(self, view))
        index = self.tabs.addTab(view, "新しいタブ")

        view.titleChanged.connect(lambda title, item=view: self.update_tab_title(item, title))
        view.urlChanged.connect(lambda current, item=view: self.update_address(item, current))
        view.loadProgress.connect(self.update_progress)
        view.loadFinished.connect(self.load_finished)
        view.page().linkHovered.connect(self.statusBar().showMessage)

        view.setUrl(url or QUrl(HOME_URL))
        if switch:
            self.tabs.setCurrentIndex(index)
        return view

    def new_tab(self):
        self.add_tab(QUrl(HOME_URL), switch=True)

    def close_tab(self, index):
        if self.tabs.count() == 1:
            self.current_view().setUrl(QUrl(HOME_URL))
            return
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        widget.deleteLater()

    def navigate(self):
        self.current_view().setUrl(QUrl(address_to_url(self.address_bar.text())))

    def go_back(self):
        self.current_view().back()

    def go_forward(self):
        self.current_view().forward()

    def reload(self):
        self.current_view().reload()

    def go_home(self):
        self.current_view().setUrl(QUrl(HOME_URL))

    def open_quantum_engine(self):
        host, port = self.quantum_server.server_address
        self.add_tab(QUrl(f"http://{host}:{port}/twin.html"), switch=True)

    def open_drug_discovery(self):
        host, port = self.quantum_server.server_address
        self.add_tab(QUrl(f"http://{host}:{port}/drug-discovery.html"), switch=True)

    def sync_current_tab(self):
        view = self.current_view()
        if view:
            self.address_bar.setText(view.url().toString())
            self.setWindowTitle(f"{view.title() or '新しいタブ'} — Multiverse")

    def update_tab_title(self, view, title):
        index = self.tabs.indexOf(view)
        if index >= 0:
            self.tabs.setTabText(index, (title or "新しいタブ")[:24])
        if view is self.current_view():
            self.setWindowTitle(f"{title or '新しいタブ'} — Multiverse")

    def update_address(self, view, url):
        if view is self.current_view():
            self.address_bar.setText(url.toString())
            self.address_bar.setCursorPosition(0)

    def update_progress(self, value):
        self.progress.setValue(value)
        self.progress.setVisible(value < 100)

    def load_finished(self, success):
        self.progress.hide()
        if not success:
            self.statusBar().showMessage("ページを読み込めませんでした", 5000)

    def handle_download(self, download: QWebEngineDownloadRequest):
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation
        )
        suggested = Path(default_dir) / download.suggestedFileName()
        destination, _ = QFileDialog.getSaveFileName(
            self, "ファイルを保存", str(suggested)
        )
        if not destination:
            download.cancel()
            return

        path = Path(destination)
        download.setDownloadDirectory(str(path.parent))
        download.setDownloadFileName(path.name)
        download.accept()
        self.statusBar().showMessage(f"ダウンロード中: {path.name}", 5000)

    def closeEvent(self, event):
        self.quantum_server.shutdown()
        self.quantum_server.server_close()
        self.quantum_thread.join(timeout=2)
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Multiverse Browser")
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
