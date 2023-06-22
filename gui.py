import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QImage

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Image Annotation Tool")
        
        self.image_dir = None
        self.image_files = []
        self.current_image_index = -1
        self.bboxes = []
        self.selected_bbox = None
        self.resizing = False
        self.image_label = QLabel(self)
        self.image_data = None # this should hold the current image data
        # self.resize(800, 600)

        # Create a QPushButton
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.clicked.connect(self.browse_folder)
        self.btn_browse.setFixedWidth(100)

        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self.next_image)
        self.btn_next.setFixedWidth(100)

        self.btn_prev = QPushButton("Previous")
        self.btn_prev.clicked.connect(self.previous_image)
        self.btn_prev.setFixedWidth(100)

        self.btn_run_detector = QPushButton("Run Detector")
        self.btn_run_detector.clicked.connect(self.run_detector)  # Connect to the function that runs the YOLO detector
        self.btn_run_detector.setFixedWidth(100)
        
        self.btn_add_label = QPushButton("Add Label")
        # self.btn_add_label.clicked.connect()  # Connect to the function that lets you manually add labels
        self.btn_add_label.setFixedWidth(100)

        self.btn_associate_label = QPushButton("Associate Label")
        # self.btn_associate_label.clicked.connect()  # Connect to the function that lets you associate labels
        self.btn_associate_label.setFixedWidth(100)

        self.resize_button = QPushButton("Resize", self)
        self.resize_button.clicked.connect(self.resize_bbox)
        self.resize_button.setFixedWidth(100)


        self.image_label = QLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setScaledContents(True)
        self.image_label.setPixmap(QPixmap(''))

        # Create a QVBoxLayout instance for buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.btn_browse)
        button_layout.addWidget(self.btn_next)
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_run_detector)
        button_layout.addWidget(self.btn_add_label)
        button_layout.addWidget(self.btn_associate_label)
        button_layout.addWidget(self.resize_button)

        # Create a QHBoxLayout instance for the overall layout
        layout = QHBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.image_label)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def browse_folder(self):
        self.image_dir = QFileDialog.getExistingDirectory(self, 'Open directory', '/home')
        if self.image_dir:
            self.image_files = sorted([f for f in os.listdir(self.image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            self.current_image_index = -1
            self.next_image()


    def next_image(self):
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()

    def previous_image(self):
        if self.image_files and self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()

    def load_image(self):
        if self.image_files:
            image_file = self.image_files[self.current_image_index]
            pixmap = QPixmap(os.path.join(self.image_dir, image_file))
            self.image_label.setPixmap(pixmap)

    def run_detector(self):
        from yolo import run_yolo
        from bbox import BoundingBox
        if self.image_files:
            image_file = self.image_files[self.current_image_index]
            source = os.path.join(self.image_dir, image_file)
            frame, bbox_list = run_yolo(source)
            
            # Convert the OpenCV image (numpy array) to QPixmap and update QLabel
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)
            self.bboxes = [BoundingBox(bb_left, bb_top, bb_width, bb_height) for bb_left, bb_top, bb_width, bb_height in bbox_list]

    def resize_bbox(self):
        self.resizing = not self.resizing  # Toggle resizing mode

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if any bounding box contains the clicked point
            point = event.pos()
            self.selected_bbox = None
            for bbox in self.bboxes:
                if bbox.contains(point):
                    self.selected_bbox = bbox
                    break

    def mouseMoveEvent(self, event):
        if self.resizing and self.selected_bbox is not None:
            # Resize the selected bounding box with the current mouse position
            point = event.pos()
            self.selected_bbox.resize(point)
            # Redraw the image with updated bounding boxes
            self.redraw_image()

    def redraw_image(self):
        import cv2
        # Make a copy of the image data
        image = self.image_data.copy()

        # Draw the bounding boxes on the image
        for bbox in self.bboxes:
            top_left = (bbox.x, bbox.y)
            bottom_right = (bbox.x + bbox.width, bbox.y + bbox.height)
            cv2.rectangle(image, top_left, bottom_right, color=(0, 255, 0), thickness=2)

        # Convert color order to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert the image data to QPixmap and set it to the QLabel
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())