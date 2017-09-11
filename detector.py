import cv2


class Detector:
    def __init__(self):
        self.image = None
        self.hues = []
        self.saturations = []
        self.values = []

    def update(self, image):
        self.image = image

    def is_clicked(self):
        return len(self.hues) > 0

    def get_upper(self):
        return (
            int(max(self.hues) * 1.05), int(max(self.saturations) *
                                            1.05), int(max(self.values) * 1.05)
        )

    def get_lower(self):
        return (
            int(min(self.hues) * 0.98), int(min(self.saturations) *
                                            0.98), int(min(self.values) * 0.98)
        )

    def mouse_callback(self, e, x, y, m, n):
        if self.image is not None:
            if e == cv2.EVENT_LBUTTONDOWN:
                pixel = self.image[y, x]
                self.hues.append(pixel[0])
                self.saturations.append(pixel[1])
                self.values.append(pixel[2])
            elif e == cv2.EVENT_RBUTTONDOWN:
                if self.is_clicked():
                    self.hues.pop()
                    self.saturations.pop()
                    self.values.pop()


class Crop:
    def __init__(self):
        self.image = None
        self.finished = False
        self.point1 = None
        self.point2 = None
        self.cursor = None

    def update(self, image):
        self.image = image

    def mouse_callback(self, e, x, y, m, n):
        if self.image is not None:
            self.cursor = (x, y)
            if e == cv2.EVENT_LBUTTONDOWN:
                self.point1 = (y, x)
            if e == cv2.EVENT_LBUTTONUP:
                self.point2 = (y, x)
                self.finished = True

    def config(self, camera):
        cv2.namedWindow("crop it", cv2.WINDOW_NORMAL)
        print "Please crop your field in image"
        cv2.setMouseCallback("crop it", self.mouse_callback)
        while not self.finished:
            _, image = camera.read()
            self.update(image)
            if self.point1:
                cv2.rectangle(image, self.point1[::-1], self.cursor, (100, 200, 100))
            cv2.imshow("crop it", image)
            cv2.waitKey(1)
        cv2.destroyWindow("crop it")

    def crop_points(self):
        return self.point1, self.point2
