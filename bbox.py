class BoundingBox:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point):
        x = point.x()
        y = point.y()
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def resize(self, point):
        x, y = point
        self.width = max(0, x - self.x)
        self.height = max(0, y - self.y)