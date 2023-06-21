import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QFileDialog, QLabel, QWidget
from PyQt5.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Image Annotation Tool")

        # Create a QPushButton
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.clicked.connect(self.browse_file)

        self.btn_run_detector = QPushButton("Run Detector")
        # self.btn_run_detector.clicked.connect()  # Connect to the function that runs the YOLO detector

        self.btn_add_label = QPushButton("Add Label")
        # self.btn_add_label.clicked.connect()  # Connect to the function that lets you manually add labels

        self.btn_associate_label = QPushButton("Associate Label")
        # self.btn_associate_label.clicked.connect()  # Connect to the function that lets you associate labels

        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap(''))

        # Create a QVBoxLayout instance
        layout = QVBoxLayout()
        layout.addWidget(self.btn_browse)
        layout.addWidget(self.btn_run_detector)
        layout.addWidget(self.btn_add_label)
        layout.addWidget(self.btn_associate_label)
        layout.addWidget(self.image_label)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def browse_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        self.image_label.setPixmap(QPixmap(fname))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
