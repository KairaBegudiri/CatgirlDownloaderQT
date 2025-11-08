from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QProgressBar, QFileDialog, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
import requests

API_ENDPOINT = "https://nekos.moe/api/v1/random/image"


class NekoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neko Viewer QT")
        self.resize(600, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        self.image_label = QLabel("No pictures yet")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #1e1e2e; color: #f5e0dc;")
        self.image_label.setMinimumHeight(400)
        main_layout.addWidget(self.image_label)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #313244;
                color: #f5e0dc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #b4befe;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.progress)

        bottom_layout = QHBoxLayout()
        self.nsfw_checkbox = QCheckBox("Allow NSFW content")

        self.refresh_button = QPushButton("Fetch New Image")
        self.download_button = QPushButton("Download")
        self.download_button.setDisabled(True)

        for btn in (self.refresh_button, self.download_button):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #b4befe;
                    color: #1e1e2e;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #cba6f7;
                }
                QPushButton:disabled {
                    background-color: #585b70;
                    color: #a6adc8;
                }
            """)

        self.refresh_button.clicked.connect(self.load_image)
        self.download_button.clicked.connect(self.save_image)

        bottom_layout.addWidget(self.nsfw_checkbox)
        bottom_layout.addWidget(self.refresh_button)
        bottom_layout.addWidget(self.download_button)
        main_layout.addLayout(bottom_layout)

        self.pixmap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_progress)
        self.progress_value = 0

    def animate_progress(self):
        self.progress_value = (self.progress_value + 5) % 105
        self.progress.setValue(self.progress_value)

    def load_image(self):
        self.refresh_button.setDisabled(True)
        self.download_button.setDisabled(True)
        self.progress.setValue(0)
        self.timer.start(50)

        nsfw_enabled = self.nsfw_checkbox.isChecked()
        url = API_ENDPOINT + ("?nsfw=true" if nsfw_enabled else "?nsfw=false")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("images"):
                self.image_label.setText("Image not found")
                return

            image_id = data["images"][0]["id"]
            image_url = f"https://nekos.moe/image/{image_id}"

            img_data = requests.get(image_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)

            self.pixmap = pixmap
            self.update_scaled_image()
            self.download_button.setDisabled(False)

        except Exception as e:
            self.image_label.setText(f"Hata oluştu: {e}")
        finally:
            self.timer.stop()
            self.progress.setValue(100)
            self.refresh_button.setDisabled(False)

    def save_image(self):
        if not self.pixmap:
            QMessageBox.warning(self, "Warning", "There are no images to download yet.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save the Image", "neko.png", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )
        if file_path:
            self.pixmap.save(file_path)
            QMessageBox.information(self, "Saved!", "The image was saved successfully!")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scaled_image()

    def update_scaled_image(self):
        if self.pixmap:
            scaled = self.pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("No pictures yet")


if __name__ == "__main__":
    app = QApplication([])
    window = NekoApp()
    window.show()
    app.exec()
