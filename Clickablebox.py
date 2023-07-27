from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen
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
        self.active_corner = None


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for i, rect in enumerate(self.rectangles):
                if QRect(rect['min_xy'], rect['max_xy']).contains(event.pos()):
                    
                    self.selected_rectangle_index = i
                    if self.parent.image_label.clicked_rect_index:
                        past_index = self.parent.image_label.clicked_rect_index.pop()
                        self.rectangles[past_index]['focus'] = False
                        self.parent.image_label.clicked_rect_index.append(i)
                        
                    rect['focus'] = True
                    print("You click box at {}".format(i))
                    break
            #for else statement
            #The “else” block only executes when there is no break in the loop.
            else:
                if self.parent.btn_add_label.isChecked():
                    self.start_pos = event.pos()
                    self.end_pos = event.pos()  # Also initialize end_pos here
                    self.drawing = True

            self.last_pos = event.pos()


    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_pos = event.pos()
   
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
            self.rectangles.append({"min_xy":self.start_pos, "max_xy":self.end_pos, 'id':None, 'focus':False})  # Store the rectangle's coordinates
            self.update()
            print(self.rectangles)
            self.parent.bbox_list_widget.addItem(str((self.start_pos.x(), self.start_pos.y(), self.end_pos.x() - self.start_pos.x(), self.end_pos.y() - self.start_pos.y())))  # Update the list widget


        elif self.selected_rectangle_index is not None:
            rect = self.rectangles[self.selected_rectangle_index]
            self.update()
            rect['focus'] = False
            if rect['id'] is None:
                new_item_text = str((rect['min_xy'].x(), rect['min_xy'].y(), rect['max_xy'].x() - rect['min_xy'].x(), rect['max_xy'].y() - rect['min_xy'].y()))
            elif rect['id'] is not None:
                new_item_text = str((rect['min_xy'].x(), rect['min_xy'].y(), rect['max_xy'].x() - rect['min_xy'].x(), rect['max_xy'].y() - rect['min_xy'].y())) + f", {rect['id']}"
            self.parent.bbox_list_widget.item(self.selected_rectangle_index).setText(new_item_text)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        font = painter.font()
        font.setPointSize(14)  # You can adjust the size as needed
        painter.setFont(font)
        for rect in self.rectangles:
            pen = QPen(Qt.green, 1)
            if rect['focus']:
                pen = QPen(Qt.red, 2)

            painter.setPen(pen)
            if rect['id'] is not None:  # Check if this rectangle has an ID
                bbox_id = rect['id']
                # Calculate center x coordinate of the bounding box
                center_x = rect['min_xy'].x() + ((rect["max_xy"].x() - rect['min_xy'].x()) / 2)
                # Draw the text at the top center of the bounding box
                painter.drawText(int(center_x - 5), int(rect['min_xy'].y() - 5), str(bbox_id))  # The "-5" is for adjusting the position of the text
            painter.drawRect(QRect(rect["min_xy"], rect["max_xy"]))
            
        painter.end()