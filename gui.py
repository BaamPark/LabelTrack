import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QSizePolicy, QListWidget, QTextEdit
from PyQt5.QtGui import QImage
from Clickablebox import ClickableImageLabel
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import QPoint

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
        self.bbox_list_widget = QListWidget() #! list widget
        self.bbox_list_widget.setFixedWidth(200)
        self.text_widget = QTextEdit()  # New text widget
        self.text_widget.setFixedWidth(200)  # Set a fixed height
        self.text_widget.setFixedHeight(50)
        self.resize(1400, 1000)

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
        self.btn_add_label.setCheckable(True) 
        self.btn_add_label.clicked.connect(self.add_label)
        self.btn_add_label.setFixedWidth(100)

        self.btn_associate_label = QPushButton("Associate Label")
        # self.btn_associate_label.clicked.connect()  # Connect to the function that lets you associate labels
        self.btn_associate_label.setFixedWidth(100)

        self.btn_remove_label = QPushButton("Remove Label")
        self.btn_remove_label.clicked.connect(self.remove_label)
        self.btn_remove_label.setFixedWidth(100)

        self.image_label = ClickableImageLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setPixmap(QPixmap(''))


        # Create a QVBoxLayout instance for buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.btn_browse)
        button_layout.addWidget(self.btn_next)
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_run_detector)
        button_layout.addWidget(self.btn_add_label)
        button_layout.addWidget(self.btn_remove_label)
        button_layout.addWidget(self.btn_associate_label)
        
        # Create a QVBoxLayout for text and list widgets
        text_list_layout = QVBoxLayout()
        text_list_layout.addWidget(self.text_widget)
        text_list_layout.addWidget(self.bbox_list_widget)

        # Create a QHBoxLayout instance for the overall layout
        layout = QHBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.image_label)
        layout.addLayout(text_list_layout)

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
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio) #! it fit the image to GUI so it doesn't show the original size.
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.rectangles.clear() # Clear the rectangles list when a new image is loaded
            self.bbox_list_widget.clear()

    def run_detector(self):
        from yolo import run_yolo
        from Bbox import Bbox
        if self.image_files:
            image_file = self.image_files[self.current_image_index]
            source = os.path.join(self.image_dir, image_file)
            _, bbox_list = run_yolo(source)

            # Load the image into a QPixmap
            pixmap = QPixmap(source)
            image_width = pixmap.width()
            image_height = pixmap.height()

            # Scale the QPixmap to fit the QLabel
            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            scale_x = pixmap.width() / image_width
            scale_y = pixmap.height() / image_height

            # Calculate the vertical offset if any
            vertical_offset = (self.image_label.height() - pixmap.height()) / 2
            print(pixmap.height())

            # Update QLabel
            self.image_label.setPixmap(pixmap)

            # Clear the rectangles list of the image_label
            self.image_label.rectangles = [] 

            for bb_left, bb_top, bb_width, bb_height in bbox_list:
                # Convert bounding box values to int
                org_left = int(bb_left)
                org_top = int(bb_top)
                org_width = int(bb_width)
                org_height = int(bb_height)

                # Convert the coordinates to the QLabel's coordinate system
                left = int(org_left * scale_x)
                top = int((org_top * scale_y) + vertical_offset)
                width = int(org_width * scale_x)
                height = int(org_height * scale_y)

                # Add the bounding box to the image_label's rectangles list and to the list widget
                rect = (QPoint(left, top), QPoint(left + width, top + height))
                self.image_label.rectangles.append(rect)
                self.bbox_list_widget.addItem(str((left, top, left + width, top + height)))  # add the coordinates to the list widget

            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.update()

    def add_label(self):
        if self.btn_add_label.isChecked():
            print("Add label checked")
            self.image_label.drawing = True
        else:
            print("Add label unchecked")
            self.image_label.drawing = False

    def remove_label(self):
        # Get the current item from the QListWidget
        item = self.bbox_list_widget.currentItem()

        if item:
            # Convert the string coordinates back to tuples
            coords = tuple(map(int, item.text()[1:-1].split(', ')))
            rect = (QPoint(coords[0], coords[1]), QPoint(coords[2], coords[3]))
            # Remove the item from QListWidget
            self.bbox_list_widget.takeItem(self.bbox_list_widget.row(item))

            # Remove the corresponding rectangle from self.image_label.rectangles
            self.image_label.rectangles.remove(rect) 

            # Repaint the QLabel
            self.image_label.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())