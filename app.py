import os
import shutil
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QLabel, QLineEdit,
                               QHBoxLayout, QFileDialog, QFrame)
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QFont

class ModernButton(QPushButton):
    def __init__(self, text, accent=False, parent=None):
        super().__init__(text, parent)
        self.accent = accent
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        if self.accent:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    border: none;
                }
                QPushButton:hover { background-color: #2563eb; }
                QPushButton:pressed { background-color: #1d4ed8; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #f1f5f9;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                    border: 1px solid #334155;
                }
                QPushButton:hover { background-color: #334155; }
            """)

class FileOrganizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dosya Düzenleyici")
        self.setFixedSize(450, 320)
        
        font_family = "Segoe UI" if sys.platform == "win32" else "sans-serif"
        self.setFont(QFont(font_family, 10))

        self.init_ui()
        self.setup_categories()

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QWidget { color: #f1f5f9; }
            QLineEdit {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px;
            }
            QLabel#Title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
            QLabel#Status { color: #94a3b8; font-size: 12px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Dosya Düzenleyici")
        title.setObjectName("Title")
        layout.addWidget(title)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        
        self.browse_btn = ModernButton("Gözat")
        self.browse_btn.clicked.connect(self.select_folder)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        self.status_label = QLabel("Hazır.")
        self.status_label.setObjectName("Status")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.scan_button = ModernButton("Düzenlemeyi Başlat", accent=True)
        self.scan_button.clicked.connect(self.start_organizing)
        layout.addWidget(self.scan_button)

    def setup_categories(self):
        self.categories = {
            "Videolar": ['.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm', '.wmv'],
            "Resimler": ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp'],
            "Arşivler": ['.zip', '.rar', '.7z', '.tar', '.gz'],
            "Belgeler": ['.pdf', '.docx', '.doc', '.xlsx', '.pptx', '.txt', '.md'],
            "Kurulum": ['.exe', '.msi', '.iso', '.apk'],
            "Kod": ['.py', '.js', '.html', '.css', '.json', '.cpp', '.sh', '.bat'],
            "Müzik": ['.mp3', '.wav', '.flac', '.m4a'],
        }
        self.reserved = list(self.categories.keys()) + ["Diğer"]

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seç", self.path_input.text())
        if folder: self.path_input.setText(folder)

    def start_organizing(self):
        target = self.path_input.text()
        if not os.path.exists(target): return

        self.scan_button.setEnabled(False)
        self.status_label.setText("Düzenleniyor...")
        QApplication.processEvents()

        moved = 0
        try:
            for item in os.listdir(target):
                path = os.path.join(target, item)
                if item.startswith('.') or item in self.reserved or os.path.isdir(path):
                    continue

                ext = os.path.splitext(item)[1].lower()
                cat_found = "Diğer"
                for cat, exts in self.categories.items():
                    if ext in exts:
                        cat_found = cat
                        break
                
                dest = os.path.join(target, cat_found)
                os.makedirs(dest, exist_ok=True)
                try:
                    shutil.move(path, os.path.join(dest, item))
                    moved += 1
                except: pass

            self.status_label.setText(f"Tamamlandı: {moved} dosya düzenlendi.")
        except Exception as e:
            self.status_label.setText(f"Hata: {str(e)}")
        
        self.scan_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    window = FileOrganizer()
    window.show()
    sys.exit(app.exec())
