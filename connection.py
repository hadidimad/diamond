import bluetooth

class Connection:
    def __init__(self,address):
        self.sock = None
        self.address = address
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.address,1))

    def send_move_angle(self,angle, speed):
        angle1 = 0
        angle2 = 0
        if angle > 180:
            angle1 = 180
            angle2 = angle - 180
        else:
            angle1 = angle

        a = [chr(250), chr(angle1), chr(angle2), chr(250)]
        for i in a:
            self.sock.send(i)
        a = [chr(210), chr(speed), chr(speed), chr(210)]
        for i in a:
            self.sock.send(i)
        a = [chr(195), chr(12), chr(12), chr(195)]
        for i in a:
            self.sock.send(i)
