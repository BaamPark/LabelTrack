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
        self.image_annotations = {}
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
        self.text_widget.setFixedHeight(25)

        self.id_widget = QTextEdit()  # New text widget
        self.id_widget.setFixedWidth(200)  # Set a fixed height
        self.id_widget.setFixedHeight(25)
        
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

        self.btn_export_label = QPushButton("Export Labels")
        self.btn_export_label.clicked.connect(self.export_labels)
        self.btn_export_label.setFixedWidth(100)

        self.btn_remove_label = QPushButton("Remove Label")
        self.btn_remove_label.clicked.connect(self.remove_label)
        self.btn_remove_label.setFixedWidth(100)

        self.btn_edit_text = QPushButton("Edit Text")  # Create the button
        self.btn_edit_text.clicked.connect(self.edit_text)  # Connect it to the function that will handle the button click
        self.btn_edit_text.setFixedWidth(100)  # Set the button width

        self.image_label = ClickableImageLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setPixmap(QPixmap(''))

        self.saved_image_label = QLabel(self)  #!
        self.saved_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.saved_image_label.setMaximumWidth(200)
        self.saved_image_label.setMaximumHeight(200)
        self.saved_image_label.setPixmap(QPixmap(''))

        self.btn_next_id = QPushButton("Next ID")
        self.btn_next_id.clicked.connect(self.next_id) #!
        self.btn_next_id.setFixedWidth(100)

        self.btn_prev_id = QPushButton("Prev ID")
        self.btn_prev_id.clicked.connect(self.previous_id) #!
        self.btn_prev_id.setFixedWidth(100)

        self.btn_enter_id = QPushButton("Enter ID") # New text widget
        self.btn_enter_id.clicked.connect(self.enter_id) #!
        self.btn_enter_id.setFixedWidth(100)

        # Create a QVBoxLayout instance for buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.btn_browse)
        button_layout.addWidget(self.btn_next)
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_run_detector)
        button_layout.addWidget(self.btn_add_label)
        button_layout.addWidget(self.btn_remove_label)
        button_layout.addWidget(self.btn_export_label)
                
        # Create a QVBoxLayout for text and list widgets
        text_list_layout = QVBoxLayout()
        text_list_layout.addWidget(self.text_widget)
        text_list_layout.addWidget(self.btn_edit_text)
        text_list_layout.addWidget(self.bbox_list_widget)
        
        text_list_layout.addWidget(self.id_widget)
        text_list_layout.addWidget(self.btn_enter_id)
        text_list_layout.addWidget(self.btn_next_id)
        text_list_layout.addWidget(self.btn_prev_id)
        text_list_layout.addWidget(self.saved_image_label) #!
        

        # Create a QHBoxLayout instance for the overall layout
        layout = QHBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.image_label)
        layout.addLayout(text_list_layout)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # self.load_saved_image("saved IDs/ID124/frameframe_num_videoview.jpg")

    def export_labels(self):
        #self.image_annotations[image_file][]
        #{'160418_above-022400.jpg': ['(339, 124, 320, 588), 123'], '170804-above bed-009600.jpg': ['(278, 263, 208, 460), 123', '(608, 373, 244, 282), 124', '(120, 313, 136, 174)'], '170814-above bed-064000.jpg': ['(665, 162, -409, 325)', '(642, 588, 180, 179)', '(796, 315, 155, 138)']}
        with open('annotations.txt', 'w') as f:
            for file, annotations in self.image_annotations.items():
                for annotation in annotations:
                    bbox, id_ = annotation.rsplit(',', 1)
                    x, y, w, h = map(int, bbox.strip('()').split(','))
                    f.write(f"{file},{id_.strip()},{x},{y},{w},{h},1,-1,-1,-1\n")
    
    def enter_id(self):
        self.id = self.id_widget.toPlainText()
        id_folder = f"saved IDs/ID{self.id}"
        if os.path.isdir(id_folder):
            # get all image files in the directory, assuming they are jpg
            self.id_image_files = sorted([f for f in os.listdir(id_folder) if f.endswith(".jpg")])
            if self.id_image_files:  # if there are images in the directory
                self.id_current_image_index = 0
                self.load_saved_image(os.path.join(id_folder, self.id_image_files[self.id_current_image_index]))
                
    def next_id(self):
        if self.id_image_files and self.id_current_image_index < len(self.id_image_files) - 1:
            # increment the index
            self.id_current_image_index += 1
            # load the image
            self.load_saved_image(os.path.join(f"saved IDs/ID{self.id}", self.id_image_files[self.id_current_image_index]))
    def previous_id(self):
        if self.id_image_files and self.id_current_image_index < len(self.id_image_files) - 1:
            # increment the index
            self.id_current_image_index -= 1
            # load the image
            self.load_saved_image(os.path.join(f"saved IDs/ID{self.id}", self.id_image_files[self.id_current_image_index]))

    def load_saved_image(self, img_path): #!
        # A new function for loading the image
        pixmap = QPixmap(img_path)
        self.saved_image_label.setPixmap(pixmap)

    def browse_folder(self):
        self.image_dir = QFileDialog.getExistingDirectory(self, 'Open directory', '/home')
        if self.image_dir:
            self.image_files = sorted([f for f in os.listdir(self.image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            self.current_image_index = -1
            self.next_image()

    def next_image(self):
        if self.image_files:
            
            self.image_annotations[self.image_files[self.current_image_index]] = [self.bbox_list_widget.item(i).text() for i in range(self.bbox_list_widget.count())]
           
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()

    def previous_image(self):
        if self.image_files:
            self.image_annotations[self.image_files[self.current_image_index]] = [self.bbox_list_widget.item(i).text() for i in range(self.bbox_list_widget.count())]
        if self.image_files and self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()

    def load_image(self):
        if self.image_files:
            image_file = self.image_files[self.current_image_index]
            pixmap = QPixmap(os.path.join(self.image_dir, image_file))
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio) 
            self.image_label.setPixmap(scaled_pixmap)

            self.image_label.rectangles.clear() # Clear the rectangles list when a new image is loaded
            if image_file in self.image_annotations:
                self.bbox_list_widget.clear()
                for bbox in self.image_annotations[image_file]:
                    self.bbox_list_widget.addItem(bbox)
                    splited_string = [s.strip() for s in bbox.replace('(', '').replace(')', '').split(',')]
                    if len(splited_string) == 4:
                        x, y, w, h = map(int, splited_string)
                        rect = (QPoint(x, y), QPoint(x + w, y + h))
                    else:
                        x, y, w, h, id = map(int, splited_string)
                        rect = (QPoint(x, y), QPoint(x + w, y + h), id)
                    self.image_label.rectangles.append(rect)

            else:
                self.bbox_list_widget.clear()

    def run_detector(self):
        from yolo import run_yolo
        from Bbox import Bbox

        if self.image_files:
            image_file = self.image_files[self.current_image_index]
            source = os.path.join(self.image_dir, image_file)
            _, bbox_list = run_yolo(source)
            print("look here", bbox_list)

            # Load the image into a QPixmap
            scale_x, scale_y, vertical_offset = self.calculate_scale_and_offset(source)

            pixmap = QPixmap(source)
            # Scale the QPixmap to fit the QLabel
            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            scale_x, scale_y, vertical_offset = self.calculate_scale_and_offset(source)

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

                # Check if this bounding box already exists in the list widget
                bbox_str = str((left, top, width, height))
                existing_items = [self.bbox_list_widget.item(i).text() for i in range(self.bbox_list_widget.count())]
                rect = (QPoint(left, top), QPoint(left + width, top + height))
                self.image_label.rectangles.append(rect)

                if bbox_str in existing_items:
                    continue  # Skip this bounding box

                result_string = [s.strip() for s in bbox_str.replace('(', '').replace(')', '').split(',')] #'(left, top, width, height), ID' => '(left, top, width, height)'
                print("box str here",bbox_str)
                print("result string here ",result_string)
                
                bbox_short = "({}, {}, {}, {})".format(result_string[0], result_string[1], result_string[2], result_string[3])
                
                found = False
                for items in existing_items:
                    if bbox_short in items:
                        print(items)
                        print("bbox short here",bbox_short)
                        found = True
                        break
                if found:
                    continue
                # Add the bounding box to the image_label's rectangles list and to the list widget
                
                self.bbox_list_widget.addItem(bbox_str)

            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.update()

    # def run_detector(self):
    #     from yolo import run_yolo
    #     from Bbox import Bbox
    #     if self.image_files:
    #         image_file = self.image_files[self.current_image_index]
    #         source = os.path.join(self.image_dir, image_file)
    #         _, bbox_list = run_yolo(source)
    #         print("look here", bbox_list)

    #         # Load the image into a QPixmap
    #         scale_x, scale_y, vertical_offset = self.calculate_scale_and_offset(source)

    #         pixmap = QPixmap(source)
    #         # Scale the QPixmap to fit the QLabel
    #         pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
    #         scale_x, scale_y, vertical_offset = self.calculate_scale_and_offset(source)

    #         # Update QLabel
    #         self.image_label.setPixmap(pixmap)

    #         # Clear the rectangles list of the image_label
    #         self.image_label.rectangles = [] 

    #         for bb_left, bb_top, bb_width, bb_height in bbox_list:
    #             # Convert bounding box values to int
    #             org_left = int(bb_left)
    #             org_top = int(bb_top)
    #             org_width = int(bb_width)
    #             org_height = int(bb_height)

    #             # Convert the coordinates to the QLabel's coordinate system
    #             left = int(org_left * scale_x)
    #             top = int((org_top * scale_y) + vertical_offset)
    #             width = int(org_width * scale_x)
    #             height = int(org_height * scale_y)

    #             # Add the bounding box to the image_label's rectangles list and to the list widget
    #             rect = (QPoint(left, top), QPoint(left + width, top + height))
    #             self.image_label.rectangles.append(rect)
    #             self.bbox_list_widget.addItem(str((left, top, width, height)))  # add the coordinates to the list widget

    #         pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
    #         self.image_label.update()

    def add_label(self):
        if self.btn_add_label.isChecked():
            self.image_label.drawing = True
        else:
            self.image_label.drawing = False

    def remove_label(self):
        # Get the current item from the QListWidget
        item = self.bbox_list_widget.currentItem()

        if item:
            splited_string = [s.strip() for s in item.text().replace('(', '').replace(')', '').split(',')]
            if len(splited_string) > 4:
                id = splited_string.pop()
                
                coords = [int(part.strip()) for part in splited_string]
                coords = xyhw_to_xyxy(coords)
                rect = (QPoint(coords[0], coords[1]), QPoint(coords[2], coords[3]), id)

            else:
                coords = [int(part.strip()) for part in splited_string]
                coords = xyhw_to_xyxy(coords)
                rect = (QPoint(coords[0], coords[1]), QPoint(coords[2], coords[3]))

            # Remove the item from QListWidget
            self.bbox_list_widget.takeItem(self.bbox_list_widget.row(item))

            # Remove the corresponding rectangle from self.image_label.rectangles
            self.image_label.rectangles.remove(rect)

            # Repaint the QLabel
            self.image_label.repaint()

    def edit_text(self):
        image_file = self.image_files[self.current_image_index]
        source = os.path.join(self.image_dir, image_file)
        # Get the current text from the QTextEdit widget
        new_text = self.text_widget.toPlainText()

        scale_x, scale_y, vertical_offset = self.calculate_scale_and_offset(source)

        # Get the currently selected item from the QListWidget
        current_item = self.bbox_list_widget.currentItem()

        # If an item is selected, update its text
        if current_item is not None:
            current_text = current_item.text()
            splited_string = current_text.replace('(', '').replace(')', '').split(',')
            if len(splited_string) > 4:
                splited_string = splited_string[:4]
                current_text = "({},{},{},{})".format(splited_string[0], splited_string[1], splited_string[2], splited_string[3])

            current_item.setText(current_text + ', ' + new_text)  # append the new text after a comma for separation
            
            left, top, width, height = map(int, splited_string)
            vertices = [left, top, width, height]
            vertices = xyhw_to_xyxy(vertices)
            right, bottom = vertices[2], vertices[3]

            capture_bbox(vertices, source, scale_x, scale_y, vertical_offset, new_text, self.current_image_index, self.image_dir)

            # Update the rectangles list with the bounding box ID
            # it has use for loop because whenever you update iamge_label, the paintEvent work same jobs again.
            for i, rect in enumerate(self.image_label.rectangles):
                if rect[0] == QPoint(left, top) and rect[1] == QPoint(right, bottom):
                    self.image_label.rectangles[i] = (rect[0], rect[1], new_text)
                    break

        # Force a repaint
        self.image_label.update()

    def calculate_scale_and_offset(self, source):
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

        return scale_x, scale_y, vertical_offset

def xyhw_to_xyxy(coords, reverse=False):
    if not reverse:
        coords[2], coords[3] = coords[2] + coords[0], coords[3] + coords[1]
    else:
        coords[2], coords[3] = coords[2] - coords[0], coords[3] - coords[1]
    return coords

#this function will be called when text edit button is pressed
def capture_bbox(bbox, source_path, scale_x, scale_y, vertical_offset, id, frame_num, image_dir):
    import cv2
    # Read the image into a numpy array
    source_image = cv2.imread(source_path)

    # Reverse the scaling and offset
    original_bbox = [int(bbox[0] / scale_x),  # left
                     int((bbox[1] - vertical_offset) / scale_y),  # top
                     int(bbox[2] / scale_x),  # right
                     int((bbox[3] - vertical_offset) / scale_y)]  # bottom

    # Crop the bounding box from the original image
    bbox_image = source_image[original_bbox[1]:original_bbox[3], original_bbox[0]:original_bbox[2]]

    os.makedirs("saved IDs/ID{}".format(id), exist_ok=True)

    output_path = "saved IDs/ID{}/frame{}_{}.jpg".format(id, frame_num, image_dir[-2:])  # replace with your desired output path

    cv2.imwrite(output_path, bbox_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())