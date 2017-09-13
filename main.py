import cv2
from colorDetector import ColorDetector
from robot import *
from detector import Crop
from connection import Connection
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--device", required=False, default=0, type=int, help="camera device")
ap.add_argument("-c", "--calibrate", action='store_true', default=False, required=False, help="re-calibrate colors")
args = vars(ap.parse_args())

camera = cv2.VideoCapture(int(args["device"]))
color_detect = ColorDetector("./colors.json")

if bool(args["calibrate"]):
    color_detect.calibrate(camera)
color_detect.load_colors()

ground = Crop()
ground.config(camera)

red_zone = RedZone()
red_zone.config(camera, ground)

robot = Robot("yellow", "blue", red_zone)
robot.connection = Connection("20:16:05:30:49:79")
robot.connection.on = True
robot.connection.connect()
cv2.namedWindow("camera", cv2.WINDOW_NORMAL)

while True:
    _, image = camera.read()
    image = cv2.bilateralFilter(image, 9, 75, 75)
    (crop_p1, crop_p2) = ground.crop_points()
    image = image[crop_p1[0]:crop_p2[0], crop_p1[1]:crop_p2[1]]
    out = image.copy()
    things = color_detect.find_things(out)
    robot.find(things)
    things = red_zone.check_things(things)
    robot.draw(out)
    robot.update_image(image)
    robot.update_maze(things)
    for i in robot.maze:
        print i
    print "----------------------------------"
    robot.draw_grid(out)
    finded = robot.choose_target(things)
    if finded:
        cv2.line(out, (robot.hx, robot.hy), (robot.target.cx, robot.target.cy), (0, 255, 255), 1)
        mx, my = robot.find_move_point(out)
        #robot.move_to_point((mx, my),out)
        if distance((mx, my), (robot.hx, robot.hy)) > 50:
            robot.move(angle((mx, my), (robot.hx, robot.hy)))
        else:
            print "here"
            robot.move(angle((robot.target.cx,robot.target.cy),(red_zone.x,red_zone.y)))
            #robot.connection.send_move_angle(0, 0)

        print "robot", robot.get_angle()
        cv2.line(out, (robot.hx, robot.hy), (mx, my), (255, 0, 255), 1)
        cv2.line(out, (robot.red_zone.x, robot.red_zone.y), (robot.target.cx, robot.target.cy), (0, 0, 255), 1)
    else:

        w, h = image.shape[:2]
        robot.move(angle((w / 2, h / 2), (robot.hx, robot.hy)))
    cv2.imshow("camera", out)
    key = cv2.waitKey(1)
    if key == 27:
        break
camera.release()
cv2.destroyAllWindows()
