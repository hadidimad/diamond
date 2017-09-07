import cv2
from colorDetector import ColorDetector
from robot import *
from detector import Crop

camera = cv2.VideoCapture(1)
color_detect = ColorDetector("./colors.json")

inp = raw_input("do you want to recalibrate colors? [y/n]")
if inp == "y":
    color_detect.calibrate(camera)
color_detect.load_colors()

ground = Crop()
ground.config(camera)

red_zone = RedZone()
red_zone.config(camera,ground)

robot = Robot("blue","green",red_zone)
cv2.namedWindow("camera",cv2.WINDOW_NORMAL)

while True:
    _, image = camera.read()
    image =  cv2.bilateralFilter(image,9,75,75)
    (crop_p1, crop_p2) = ground.crop_points()
    image = image[crop_p1[0]:crop_p2[0], crop_p1[1]:crop_p2[1]]
    out = image.copy()
    things = color_detect.find_things(out)
    things=red_zone.check_things(things)
    robot.find(things)
    robot.draw(out)
    robot.update_image(image)
    robot.update_maze(things)
    #for i in robot.maze:
    #    print i
    #print "----------------------------------"
    robot.draw_grid(out)
    robot.choose_goal(things)
    cv2.line(out,(robot.hx,robot.hy),(robot.goal.cx,robot.goal.cy),(0,0,255),1)
    mx,my=robot.find_move_point(out)
    cv2.line(out, (robot.hx, robot.hy), (mx, my), (255, 0, 255), 1)
    cv2.line(out, (robot.red_zone.x, robot.red_zone.y), (robot.goal.cx, robot.goal.cy), (0, 0, 255), 1)
    cv2.imshow("camera", out)
    key = cv2.waitKey(1)
    if key == 27:
        break
camera.release()
cv2.destroyAllWindows()