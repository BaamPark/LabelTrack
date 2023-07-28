from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel

class ClickableImageLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent) #https://www.educative.io/answers/what-is-super-in-python
        #This is separate from the concept of class inheritance. 
        #When the ClickableImageLabel object is created inside the MainWindow class, MainWindow becomes its parent widget.
        self.parent = parent
        self.start_pos = None
        self.end_pos = None
        self.drawing = False
        self.rectangles = []
        self.clicked_rect = []
        self.selected_rectangle_index = None
        self.last_pos = None
        self.active_rectangle_index = None
        self.active_corner = None


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.active_corner = None
            for i, rect in enumerate(self.rectangles):
                top_left = rect['min_xy']
                bottom_right = rect['max_xy']
                top_right = QPoint(bottom_right.x(), top_left.y())
                bottom_left = QPoint(top_left.x(), bottom_right.y())

                #this for loop is used for resizing the box
                for j, corner in enumerate([top_left, top_right, bottom_left, bottom_right]):
                    if (corner - event.pos()).manhattanLength() < 10:  # 10 is the max distance to detect a corner
                        self.active_rectangle_index = i
                        self.active_corner = j
                        continue

                #this if block is used for relocation
                if QRect(top_left, bottom_right).contains(event.pos()):

                    self.selected_rectangle_index = i
                    if self.parent.image_label.clicked_rect_index:
                        past_index = self.parent.image_label.clicked_rect_index.pop()
                        self.rectangles[past_index]['focus'] = False
                        self.parent.image_label.clicked_rect_index.append(i)
                        
                    rect['focus'] = True
                    break

            #for else statement: The “else” block only executes when there is no break in the loop.
            else:
                if self.parent.btn_add_label.isChecked() and self.active_corner is None:
                    self.start_pos = event.pos()
                    self.end_pos = event.pos()  # Also initialize end_pos here
                    self.drawing = True

            self.last_pos = event.pos()


    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_pos = event.pos()

        #resize mode
        elif self.active_corner is not None: 
            rect = self.rectangles[self.active_rectangle_index]
            if self.active_corner == 0:  # top left
                rect['min_xy'] = event.pos()
            elif self.active_corner == 1:  # top right
                rect['min_xy'].setY(event.pos().y())
                rect['max_xy'].setX(event.pos().x())
            elif self.active_corner == 2:  # bottom left
                rect['min_xy'].setX(event.pos().x())
                rect['max_xy'].setY(event.pos().y())
            else:  # bottom right
                rect['max_xy'] = event.pos()

        #relocation mode
        elif self.selected_rectangle_index is not None:
            offset = event.pos() - self.last_pos
            start, end = self.rectangles[self.selected_rectangle_index]['min_xy'], self.rectangles[self.selected_rectangle_index]['max_xy']
            self.rectangles[self.selected_rectangle_index]['min_xy'] = start + offset
            self.rectangles[self.selected_rectangle_index]['max_xy'] = end + offset

        self.last_pos = event.pos()
        self.update()


    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.drawing = False
            rect = {"min_xy":self.start_pos, "max_xy":self.end_pos, 'id': None, 'focus':False}
            rect = self.check_negative_box(rect)
            self.rectangles.append(rect)  # Store the rectangle's coordinates
            self.update()
            self.parent.bbox_list_widget.addItem(str((rect['min_xy'].x(), rect['min_xy'].y(), rect['max_xy'].x() - rect['min_xy'].x(), rect['max_xy'].y() - rect['min_xy'].y())))  # Update the list widget
        
        elif self.selected_rectangle_index is not None:
            rect = self.rectangles[self.selected_rectangle_index]
            self.update()
            rect['focus'] = False
            if rect['id'] is None:
                new_item_text = str((rect['min_xy'].x(), rect['min_xy'].y(), rect['max_xy'].x() - rect['min_xy'].x(), rect['max_xy'].y() - rect['min_xy'].y()))
            elif rect['id'] is not None:
                new_item_text = str((rect['min_xy'].x(), rect['min_xy'].y(), rect['max_xy'].x() - rect['min_xy'].x(), rect['max_xy'].y() - rect['min_xy'].y())) + f", {rect['id']}"
            self.parent.bbox_list_widget.item(self.selected_rectangle_index).setText(new_item_text)

    def check_negative_box(self, rect):
        print("min x: ", rect['min_xy'].x())
        print("max x", rect['max_xy'].x())
        if rect['min_xy'].x() > rect['max_xy'].x() or rect['min_xy'].y() > rect['max_xy'].y():
            rect['min_xy'], rect['max_xy'] = rect['max_xy'], rect['min_xy']
            print("min x: ", rect['min_xy'].x())
            print("max x", rect['max_xy'].x())
            return rect
        else:
            return rect

    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        font = painter.font()
        font.setPointSize(14) #the size of text for id
        painter.setFont(font)
        for rect in self.rectangles:
            top_left = rect['min_xy']
            bottom_right = rect['max_xy']
            top_right = QPoint(bottom_right.x(), top_left.y())
            bottom_left = QPoint(top_left.x(), bottom_right.y())

            pen = QPen(QColor(135, 206, 235), 1)  #sky blue rgb code
            painter.setPen(pen)
            painter.setBrush(QColor(135, 206, 235))
            for corner in [top_left, top_right, bottom_left, bottom_right]:
                circle_radius = 5
                painter.drawEllipse(corner, circle_radius, circle_radius)

            pen = QPen(Qt.green, 1)
            if rect['focus']:
                pen = QPen(Qt.red, 2)

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            if rect['id'] is not None:  # Check if this rectangle has an ID
                bbox_id = rect['id']
                # Calculate center x coordinate of the bounding box
                center_x = top_left.x() + ((bottom_right.x() - top_left.x()) / 2)
                # Draw the text at the top center of the bounding box
                painter.drawText(int(center_x - 5), int(top_left.y() - 5), str(bbox_id))  # The "-5" is for adjusting the position of the text
            painter.drawRect(QRect(top_left, bottom_right))
            
        painter.end()