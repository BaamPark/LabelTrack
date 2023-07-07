from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QLabel

class ClickableImageLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.start_pos = None
        self.end_pos = None
        self.drawing = False
        self.rectangles = []
        self.clicked_rect = []

    def mousePressEvent(self, event):
        if self.parent.btn_add_label.isChecked() and event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.drawing = False
            self.rectangles.append((self.start_pos, self.end_pos))  # Store the rectangle's coordinates
            self.update()
            print(self.rectangles)
            self.parent.bbox_list_widget.addItem(str((self.start_pos.x(), self.start_pos.y(), self.end_pos.x() - self.start_pos.x(), self.end_pos.y() - self.start_pos.y())))  # Update the list widget

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        # pen = QPen(Qt.green, 3)
        # painter.setPen(pen)
        font = painter.font()
        font.setPointSize(14)  # You can adjust the size as needed
        painter.setFont(font)
        for rect in self.rectangles:
            pen = QPen(Qt.green, 3)
            painter.setPen(pen)
            if len(rect) == 3:  # Check if this rectangle has an ID
                bbox_id = rect[2]
                print(bbox_id)
                
                # Calculate center x coordinate of the bounding box
                center_x = rect[0].x() + ((rect[1].x() - rect[0].x()) / 2)
                
                # Draw the text at the top center of the bounding box
                painter.drawText(int(center_x - 5), int(rect[0].y() - 5), str(bbox_id))  # The "-5" is for adjusting the position of the text
            painter.drawRect(QRect(rect[0], rect[1]))

        for rect in self.clicked_rect:
            pen = QPen(Qt.red, 3)
            painter.setPen(pen)
            if len(rect) == 3:  # Check if this rectangle has an ID
                bbox_id = rect[2]
                print(bbox_id)
                
                # Calculate center x coordinate of the bounding box
                center_x = rect[0].x() + ((rect[1].x() - rect[0].x()) / 2)
                
                # Draw the text at the top center of the bounding box
                painter.drawText(int(center_x - 5), int(rect[0].y() - 5), str(bbox_id))  # The "-5" is for adjusting the position of the text
            painter.drawRect(QRect(rect[0], rect[1]))
            
        painter.end()
            
    # def paintEvent(self, event):
    #     super().paintEvent(event)
    #     painter = QPainter(self)
    #     painter.setPen(QPen(Qt.red, 3))
    #     if self.drawing and self.start_pos and self.end_pos:
    #         print("Drawing")
    #         painter.drawRect(QRect(self.start_pos, self.end_pos))
    #     for rect in self.rectangles:
    #         painter.drawRect(QRect(*rect))