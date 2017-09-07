import cv2
import math
from heapq import heappop, heappush
import copy


def heuristic(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def maze2graph(self):
    height = len(self.maze)
    width = len(self.maze[0]) if height else 0
    graph = {(i, j): [] for j in range(width) for i in range(height) if not self.maze[i][j]}
    for row, col in graph.keys():
        if row < height - 1 and not self.maze[row + 1][col]:
            graph[(row, col)].append(("S", (row + 1, col)))
            graph[(row + 1, col)].append(("N", (row, col)))
        if col < width - 1 and not self.maze[row][col + 1]:
            graph[(row, col)].append(("E", (row, col + 1)))
            graph[(row, col + 1)].append(("W", (row, col)))
    return graph


def find_path_astar(maze, start, goal):
    pr_queue = []
    heappush(pr_queue, (0 + heuristic(start, goal), 0, "", start))
    visited = set()
    graph = maze2graph(maze)
    while pr_queue:
        _, cost, path, current = heappop(pr_queue)
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        for direction, neighbour in graph[current]:
            heappush(pr_queue, (cost + heuristic(neighbour, goal), cost + 1,
                                path + direction, neighbour))
    return "NO WAY!"


class Robot:
    def __init__(self, color1, color2, red_zone):
        self.hx = 0
        self.hy = 0
        self.ex = 0
        self.ey = 0
        self.angle = None
        self.color1 = color1
        self.color2 = color2
        self.offset = 300
        self.finded = False
        maze = []
        self.MAZE_MAX_X = 10
        self.MAZE_MAX_Y = 10
        for i in xrange(self.MAZE_MAX_Y):
            maze.append([])
            for j in xrange(self.MAZE_MAX_X):
                maze[i].append(0)
        self.maze = maze
        self.image = None
        self.red_zone = red_zone
        self.goal = None  # type Thing

    def draw(self, image):
        if self.finded == True:
            cv2.line(image, (self.hx, self.hy), (self.ex, self.ey), (255, 0, 0), 6)
            cv2.putText(image, "robot", (self.hx, self.hy), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 200, 100), 1, cv2.LINE_AA)

    def get_angle(self):
        return angle((self.hx, self.hy), (self.ex, self.ey))

    def update_pos(self, point1, point2):
        (x1, y1) = point1[0], point1[1]
        (x2, y2) = point2[0], point2[1]
        if distance(point1, (self.hx, self.hy)) > 5 or distance(point2, (self.ex, self.ey)) > 5:
            self.hx = x1
            self.hy = y1
            self.ex = x2
            self.ey = y2
            return True
        return False

    def find(self, things):
        for i in things:
            if i.color == self.color1:
                for j in things:
                    if j.color == self.color2:
                        (x2, y2) = j.x + j.w / 2, j.y + j.h / 2
                        (x1, y1) = i.x + i.w / 2, i.y + i.h / 2
                        if distance((x1, y1), (x2, y2)) < 50:
                            self.update_pos((x1, y1), (x2, y2))
                            things.remove(i)
                            things.remove(j)
                            self.finded = True
                            return
        self.finded = False

    def move(self, dir):
        print "move in", dir

    def keep_to_cent(self):
        w, h = self.image.shape[:2]
        mx = self.hx * (w / self.MAZE_MAX_X) + ((w / self.MAZE_MAX_X) / 2)
        my = self.hy * (h / self.MAZE_MAX_Y) + ((h / self.MAZE_MAX_Y) / 2)
        if distance((mx, my), (self.hx, self.hy)) < 5:
            return True
        else:
            self.move(angle((self.hx, self.hy), (mx, my)))
            return False
    def find_move_point(self,image):
        a = math.degrees(math.atan2((self.red_zone.y-self.goal.cy),(self.red_zone.x - self.goal.cx)))
        if a < 0:
            a = abs(a)
            a = 180 - a
            a = 180 + a
        a = abs(a - 360)
        a = int(a)
        cv2.putText(image, str(int(a)), (self.red_zone.x, self.red_zone.y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 0), 1, cv2.LINE_AA)
        a = math.radians(a)
        mx = int(self.goal.cx - (math.cos(a) * 50))
        my = int(self.goal.cy + (math.sin(a) * 50))
        return mx,my

    def choose_goal(self, things):
        a = copy.deepcopy(things)

        def compare(a, b):
            # return distance((self.hx,self.hy),(a.cx,a.cy))+distance((a.cx,a.cy),(self.red_zone.x,self.red_zone.y))
            # ""sum of robot distance to goal and object distance to red zone""
            dista=int(distance((a.cx, a.cy), (self.red_zone.x, self.red_zone.y)) - distance((b.cx, b.cy), (self.red_zone.x, self.red_zone.y)))
            return dista

        a.sort(cmp=compare)
        if len(a) == 0:
            return False
        self.goal = a[0]
        return True

    def update_image(self, image):
        self.image = image

    def convert_maze_x(self, x):
        w, h = self.image.shape[:2]
        return int(math.floor(x / (w / self.MAZE_MAX_X)))

    def convert_maze_y(self, y):
        w, h = self.image.shape[:2]
        return int(math.floor(y / (h / self.MAZE_MAX_Y)))

    def update_maze(self, things):
        for i in xrange(len(self.maze)):
            for j in xrange(len(self.maze[i])):
                self.maze[i][j] = 0
        for thing in things:
            ix = self.convert_maze_x(thing.cx)
            iy = self.convert_maze_y(thing.cy)
            if ix < self.MAZE_MAX_X and iy < self.MAZE_MAX_Y:
                self.maze[iy][ix] = 1

    def draw_grid(self, image):
        w, h = image.shape[:2]
        for i in xrange(self.MAZE_MAX_X):
            image = cv2.rectangle(image, (i * (w / self.MAZE_MAX_X), 0),
                                  (i * (w / self.MAZE_MAX_X), h), (0, 0, 255), 1)
        for i in xrange(self.MAZE_MAX_Y):
            image = cv2.rectangle(image, (0, i * (h / self.MAZE_MAX_Y)), (w, i * (h / self.MAZE_MAX_Y)), (0, 0, 255), 1)


class Thing:
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cx = x + (w / 2)
        self.cy = y + (h / 2)
        self.color = color


class RedZone:
    def __init__(self):
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.x = 0
        self.y = 0
        self.points = []
        self.image = None
        self.finished = False

    def mouse_callback(self, e, x, y, m, n):
        if self.image is not None:
            if e == cv2.EVENT_LBUTTONDOWN:
                self.points.append((x, y))
            if len(self.points) == 2:
                self.finished = True

    def config(self, camera,ground):
        cv2.namedWindow("choose red zone", cv2.WINDOW_NORMAL)
        print "please crop your red zone in image"
        cv2.setMouseCallback("choose red zone", self.mouse_callback)
        while not self.finished:
            _, image = camera.read()
            (crop_p1, crop_p2) = ground.crop_points()
            image = image[crop_p1[0]:crop_p2[0], crop_p1[1]:crop_p2[1]]
            self.image = image
            cv2.imshow("choose red zone", image)
            cv2.waitKey(1)
        cv2.destroyWindow("choose red zone")
        self.x1 = self.points[0][0]
        self.y1 = self.points[0][1]
        self.x2 = self.points[1][0]
        self.y2 = self.points[1][1]
        self.x = self.x1 + (self.x2 - self.x1) / 2
        self.y = self.y1 + (self.y2 - self.y1) / 2

    def check_things(self, things):
        for i in things:
            if (self.x1 < i.cx <= self.x2) and (self.y1 < i.cy < self.y2):
                things.remove(i)
        return things


def angle(point1, point2):
    (x1, y1) = point1
    (x2, y2) = point2
    radian = math.atan2(y2 - y1, x2 - x1)
    angle = math.degrees(radian)
    return angle


def distance(point1, point2):
    (x1, y1) = point1[0], point1[1]
    (x2, y2) = point2[0], point2[1]
    d2 = math.pow(abs(x2 - x1), 2) + math.pow(abs(y2 - y1), 2)
    dist = math.sqrt(d2)
    return dist