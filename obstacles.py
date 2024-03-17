import csv
from utils import scale_points


class BoxObstacle(object):
    def __init__(self, points):
        self.points = points  # the 4 vertices of the box

        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]

        # AABB representation
        self.x_min = min(xs)
        self.x_max = max(xs)
        self.y_min = min(ys)
        self.y_max = max(ys)

        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min

    def contains_point(self, point, scale_x, scale_y, offset_x, offset_y):
        # print("point", point)
        x_min_scaled = self.x_min * scale_x + offset_x
        x_max_scaled = self.x_max * scale_x + offset_x
        y_min_scaled = self.y_min * scale_y + offset_y
        y_max_scaled = self.y_max * scale_y + offset_y

        x, y = point
        return x_min_scaled <= x <= x_max_scaled and y_min_scaled <= y <= y_max_scaled


def load_obstacles(filename):
    obstacles = []
    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 8:
                obstacle_points = [
                    (float(row[i]), float(row[i + 1])) for i in range(0, 8, 2)
                ]
                obstacles.append(BoxObstacle(obstacle_points))
    return obstacles
