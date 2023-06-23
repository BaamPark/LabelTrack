# from PyQt5.QtWidgets import QLabel
# from PyQt5.QtGui import QPainter, QColor
# from PyQt5.QtCore import Qt
# from Bbox import BBox

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
            self.parent.bbox_list_widget.addItem(str((self.start_pos.x(), self.start_pos.y(), self.end_pos.x(), self.end_pos.y())))  # Update the list widget
            print(self.start_pos)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 3))
        if self.drawing and self.start_pos and self.end_pos:
            print("Drawing")
            painter.drawRect(QRect(self.start_pos, self.end_pos))
        for rect in self.rectangles:
            painter.drawRect(QRect(*rect))