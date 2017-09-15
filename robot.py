import cv2
import math
from heapq import heappop, heappush
import copy


def heuristic(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def maze2graph(maze):
    height = len(maze)
    width = len(maze[0]) if height else 0
    graph = {(i, j): [] for j in range(width) for i in range(height) if not maze[i][j]}
    for row, col in graph.keys():
        if row < height - 1 and not maze[row + 1][col]:
            graph[(row, col)].append(("S", (row + 1, col)))
            graph[(row + 1, col)].append(("N", (row, col)))
        if col < width - 1 and not maze[row][col + 1]:
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
        self.MAX_SPEED = 200  # at most 255
        maze = []
        self.MAZE_MAX_X = 15
        self.MAZE_MAX_Y = 15
        for i in xrange(self.MAZE_MAX_Y):
            maze.append([])
            for j in xrange(self.MAZE_MAX_X):
                maze[i].append(0)
        self.maze = maze
        self.image = None
        self.red_zone = red_zone
        self.target = None  # type Thing
        self.connection = None
        self.send_angle = 0

    def draw(self, image):
        if self.finded == True:
            cv2.line(image, (self.hx, self.hy), (self.ex, self.ey), (255, 0, 0), 6)
            cv2.putText(image, "robot", (self.hx, self.hy), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 200, 100), 1, cv2.LINE_AA)

    def get_angle(self):
        a = angle((self.hx, self.hy), (self.ex, self.ey))
        if a < 0:
            a = abs(a)
            a = 180 - a
            a = 180 + a
        a = abs(a - 360)
        a = int(a)
        return a

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
                        if distance((x1, y1), (x2, y2)) <30:
                            self.update_pos((x1, y1), (x2, y2))
                            things.remove(i)
                            things.remove(j)
                            self.finded = True
                            return
        self.finded = False

    def stop(self):
        self.connection.stop()

    def move(self, direction, speed=6):
        if direction < 0:
            direction = abs(direction)
            direction = 180 - direction
            direction = 180 + direction
        direction = abs(direction - 360)
        direction = int(direction)
        direction = direction - self.get_angle()
        if direction < 0:
            direction = abs(direction)
            direction = 180 - direction
            direction = 180 + direction
        if speed > self.MAX_SPEED:
            speed = self.MAX_SPEED
        print "move dir", direction, "speed ", speed
        self.connection.send_move_angle(direction, speed)

    def set_angle(self, direction):
        if abs(self.send_angle - direction) > 5:
            if direction < 0:
                direction = abs(direction)
                direction = 180 - direction
                direction = 180 + direction
            direction = abs(direction - 360)
            direction = int(direction)
            self.connection.set_zero_angle(direction)

    def move_to_point(self, point, image):
        (x, y) = point[0], point[1]
        if distance((self.hx, self.hy), (self.target.cx, self.target.cy)) > 100:
            self.move(angle((x, y), (self.hx, self.hy)))
        else:
            print "near"
            if self.hx - x < 0 or self.hy - y < 0:
                self.move(angle((x, y), (self.hx, self.hy)) + 90)
            else:
                self.move(angle((x, y), (self.hx, self.hy)))
            return False

    def move_target(self, image):
        x, y, back_wall = self.find_move_point((self.red_zone.x, self.red_zone.y))
        if self.red_zone.close_side == "r":
            x, y, back_wall = self.find_move_point(
                (self.red_zone.x, self.red_zone.y + (self.red_zone.y2 - self.red_zone.y1) / 2))
        elif self.red_zone.close_side == "d":
            x, y, back_wall = self.find_move_point(
                (self.red_zone.x + (self.red_zone.x2 - self.red_zone.x1) / 2, self.red_zone.y))
        print back_wall
        image = cv2.line(image, (self.hx, self.hy), (x, y), (0, 0, 0), 1)
        if distance((self.hx, self.hy), (self.target.cx, self.target.cy)) > 65:
            self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)))
        else:
            if not back_wall:
                if self.hx - x < 0 or self.hy - y < 0:
                    if self.hx - x < 0:
                        self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)) + 90)
                    elif self.hy - y < 0:
                        self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)) - 90)

                else:
                    self.move(angle((x, y), (self.hx, self.hy)))
                    if distance((x, y), (self.target.cx, self.target.cy)) < 20:
                        self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)), 9)
            else:
                if self.red_zone.close_side == "r":
                    if self.hy - y > 0:
                        self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)) + 90)
                    else:
                        self.move(angle((x, y), (self.hx, self.hy)))
                        if distance((x, y), (self.target.cx, self.target.cy)) < 20:
                            self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)))
                elif self.red_zone.close_side == "d":
                    if self.hx - x > 0:
                        self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)) - 90)
                    else:
                        self.move(angle((x, y), (self.hx, self.hy)))
                        if distance((x, y), (self.target.cx, self.target.cy)) < 20:
                            self.move(angle((self.target.cx, self.target.cy), (self.hx, self.hy)))

    def find_move_point(self, (x, y)):
        is_back_wall = False
        a = math.degrees(math.atan2((y - self.target.cy), (x - self.target.cx)))

        if a < 0:
            a = abs(a)
            a = 180 - a
            a = 180 + a
        a = abs(a - 360)
        a = int(a)
        a = math.radians(a)
        mx = int(self.target.cx - (math.cos(a) * 5))
        my = int(self.target.cy + (math.sin(a) * 5))
        return mx, my, is_back_wall

    def choose_target(self, things):
        if len(things) == 0:
            return False
        a = copy.deepcopy(things)

        def compare(a, b):
            dista = int(distance((a.cx, a.cy), (self.red_zone.x, self.red_zone.y)) - distance((b.cx, b.cy), (
                self.red_zone.x, self.red_zone.y)))
            return dista

        w, h = self.image.shape[:2]
        d = distance((self.red_zone.x1, self.red_zone.y1), (self.red_zone.x2, self.red_zone.y2))
        d = int(d / 2)
        a.sort(cmp=compare)
        f = False
        for i in a:
            if distance((i.x, i.y), (self.hx, self.hy)) < 5:
                continue
            if distance((i.x, i.y), (self.ex, self.ey)) < 5:
                continue
            if i.cx <= d:
                continue
            if i.cy <= d:
                continue
            if i.cx >= w - d:
                continue
            if i.cy >= h - d:
                continue
            self.target = i
            f = True
            break
        if not f:
            for i in a:
                if distance((i.x, i.y), (self.hx, self.hy)) < 5:
                    continue
                if distance((i.x, i.y), (self.ex, self.ey)) < 5:
                    continue
                self.target = i
                f = True
                break
        return f

    def update_image(self, image):
        self.image = image

    def convert_maze_x(self, x):
        w, h = self.image.shape[:2]
        return int(math.floor(x / (w / self.MAZE_MAX_X)))

    def convert_maze_y(self, y):
        w, h = self.image.shape[:2]
        return int(math.floor(y / (h / self.MAZE_MAX_Y)))

    def set_goal(self, point):
        (x, y) = point[0], point[1]
        self.nx = x
        self.ny = y

    def update_maze(self, things):
        for i in xrange(len(self.maze)):
            for j in xrange(len(self.maze[i])):
                self.maze[i][j] = False
        for thing in things:
            ix = self.convert_maze_x(thing.cx)
            iy = self.convert_maze_y(thing.cy)
            if ix < self.MAZE_MAX_X and iy < self.MAZE_MAX_Y:
                self.maze[iy][ix] = True

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
        self.close_side = "n"
        self.points = []
        self.image = None
        self.finished = False

    def mouse_callback(self, e, x, y, m, n):
        if self.image is not None:
            if e == cv2.EVENT_LBUTTONDOWN:
                self.points.append((x, y))
            if len(self.points) == 2:
                self.finished = True

    def config(self, camera, ground):
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
