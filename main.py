import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
from core.installer import ensure_structure
from core.shortcuts import create_all_shortcuts
from core.database import init_db
from core.analyzer import analyze_and_store_images
from core.paths import get_base_path
from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Qt
from core.design_pack import process_design_pack
from core.config import load_config, save_config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HOPS_V1")
        self.setGeometry(100, 100, 1200, 700)

        self.config = load_config()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("background-color: #111; color: #eee;")
        header.setFixedHeight(50)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)

        title = QLabel("HOPS_V1")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title, alignment=Qt.AlignLeft)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: #eee;
                padding: 6px 12px;
                border: 1px solid #333;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        self.btn_settings.clicked.connect(self.show_settings)
        header_layout.addWidget(self.btn_settings, alignment=Qt.AlignRight)

        self.main_layout.addWidget(header)

        content_area = QFrame()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet("background-color: #1a1a1a;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 10)
        sidebar_layout.setSpacing(12)

        btn_style = """
            QPushButton {
                background-color: #222;
                color: #ccc;
                padding: 10px;
                text-align: left;
                border: none;
            }
            QPushButton:hover {
                background-color: #333;
                color: #fff;
            }
        """

        btn_dashboard = QPushButton("Dashboard")
        btn_dashboard.setStyleSheet(btn_style)

        btn_analyzer = QPushButton("Analyzer")
        btn_analyzer.setStyleSheet(btn_style)
        btn_analyzer.clicked.connect(self.run_analyzer)


        sidebar_layout.addWidget(btn_dashboard)
        sidebar_layout.addWidget(btn_analyzer)
        sidebar_layout.addStretch()

        self.center_content = QFrame()
        self.center_content.setStyleSheet("background-color: #000;")
        self.center_layout = QVBoxLayout(self.center_content)

        content_layout.addWidget(sidebar)
        content_layout.addWidget(self.center_content)

        self.main_layout.addWidget(content_area)

    def clear_center(self):
        while self.center_layout.count():
            item = self.center_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                layout = item.layout()
                if layout:
                    while layout.count():
                        sub_item = layout.takeAt(0)
                        sub_widget = sub_item.widget()
                        if sub_widget:
                            sub_widget.deleteLater()

    def show_settings(self):
        self.clear_center()

        wrapper = QFrame()
        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(20, 15, 20, 15)
        vbox.setSpacing(10)

        settings_row = QFrame()
        settings_row.setStyleSheet("""
            QLabel {
                color: #eee;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #222;
                color: #eee;
                padding: 6px;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #222;
                color: #eee;
                padding: 6px 16px;
                border: 1px solid #333;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)

        hbox = QHBoxLayout(settings_row)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(15)

        lbl = QLabel("Trimming (%):")
        self.input_trim = QLineEdit(str(self.config.get("trimming", 8)))

        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self.save_settings)

        hbox.addWidget(lbl)
        hbox.addWidget(self.input_trim, 1)
        hbox.addWidget(btn_save)

        self.saved_label = QLabel("")
        self.saved_label.setStyleSheet("color: #0f0; font-size: 12px;")

        vbox.addWidget(settings_row)
        vbox.addWidget(self.saved_label)

        self.center_layout.addWidget(wrapper, alignment=Qt.AlignTop)

    def save_settings(self):
        try:
            trimming_value = int(self.input_trim.text())
        except ValueError:
            trimming_value = 8

        self.config["trimming"] = trimming_value
        save_config(self.config)

        self.saved_label.setText(f"✔ Trimming kaydedildi: %{trimming_value}")

    def run_analyzer(self):
        self.clear_center()

        wrapper = QFrame()
        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(10)

        # Label
        self.status_label = QLabel("Hazırlanıyor...")
        self.status_label.setStyleSheet("color: #0f0; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignLeft)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setFixedHeight(25)  # kalınlık ayarı
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
                color: #eee;
                background-color: #111;
            }
            QProgressBar::chunk {
                background-color: #0a0;
            }
        """)
        self.progress.setValue(0)

        vbox.addWidget(self.status_label)
        vbox.addWidget(self.progress)

        self.center_layout.addWidget(wrapper, alignment=Qt.AlignTop)

        # Görselleri al
        base = get_base_path()
        images_path = base / "0_Data"
        files = list(images_path.glob("*.*"))
        total = len(files)

        if total == 0:
            self.progress.setValue(0)
            self.status_label.setText("⚠ İşlenecek görsel bulunamadı.")
            return

        for i, f in enumerate(files, start=1):
            analyze_and_store_images()
            percent = int((i / total) * 100)
            self.progress.setValue(percent)
            self.status_label.setText(f"{i}/{total} görsel işlendi...")
            QApplication.processEvents()

        self.progress.setValue(100)
        self.status_label.setText(f"✔ {total} görsel analiz edildi ve veritabanına kaydedildi.")

def main():
    base = ensure_structure()
    create_all_shortcuts()
    init_db()
    print(f"[OK] Yapı kuruldu: {base}")


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
