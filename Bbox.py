class Bbox:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point):
        x = point.x()
        y = point.y()
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def resize_to_reach(self, point):
        self.width = max(point.x() - self.x, 0)
        self.height = max(point.y() - self.y, 0)
