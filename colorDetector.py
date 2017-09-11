import json
import cv2
import detector as dect
from robot import Thing


class ColorDetector:
    def __init__(self, filename):
        self.colors = {"yellow": ((0, 0, 0), (0, 0, 0)), "green": ((0, 0, 0), (0, 0, 0)), "blue": ((0, 0, 0), (0, 0, 0)),
                       "pink": ((0, 0, 0), (0, 0, 0))}
        self.file = filename

    def load_colors(self):
        try:
            with open(self.file, "r+") as f:
                string = f.read()
                self.colors = json.loads(string)
                print "colors loaded! [OK]"
        except IOError:
            d = json.dumps(self.colors)
            with open(self.file, "w+") as f:
                f.write(d)

    def calibrate(self, camera):
        cv2.namedWindow("calibrate color", cv2.WINDOW_NORMAL)
        for col in self.colors:
            detector = dect.Detector()
            cv2.setMouseCallback("calibrate color", detector.mouse_callback)
            print "click on " + col + " color in picture"
            while True:
                _, image = camera.read()
                image = cv2.bilateralFilter(image, 9, 75, 75)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                detector.update(hsv)

                if detector.is_clicked():
                    upper = detector.get_upper()
                    lower = detector.get_lower()
                    bw = cv2.inRange(hsv, lower, upper)
                    _, contours, hierarchy = cv2.findContours(
                        bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    if hierarchy is not None:
                        hierarchy = hierarchy[0]
                        for component in zip(contours, hierarchy):
                            currentContour = component[0]
                            currentHierarchy = component[1]
                            x, y, w, h = cv2.boundingRect(currentContour)
                            if currentHierarchy[3] < 0 and w * h > 300:
                                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.imshow("calibrate color", image)
                cv2.imshow("hsv", hsv)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    self.colors[col] = (lower, upper)
                    break
                elif key == 32:
                    upper = detector.get_upper()
                    lower = detector.get_lower()
                    print lower, upper
        string = json.dumps(self.colors)
        file = open(self.file, "w")
        file.write(string)
        file.close()
        print "colors calibrated and saved [OK]"
        cv2.destroyWindow("calibrate color")
        cv2.destroyWindow("hsv")

    def find_things(self, image):
        things = []
        for col in self.colors:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            bw = cv2.inRange(hsv, tuple(
                self.colors[col][0]), tuple(self.colors[col][1]))
            _, contours, hierarchy = cv2.findContours(
                bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if hierarchy is not None:
                hierarchy = hierarchy[0]
                for component in zip(contours, hierarchy):
                    cnt = component[0]
                    currentHierarchy = component[1]
                    x, y, w, h = cv2.boundingRect(cnt)
                    if currentHierarchy[3] < 0 and w * h > 200:
                        image = cv2.rectangle(
                            image, (x, y), (x + w, y + h), (100, 200, 100))
                        #image = cv2.putText(image, col, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        #                    (100, 200, 100), 3, cv2.LINE_AA)
                        temp = Thing(x, y, w, h, col)
                        things.append(temp)
        return things
