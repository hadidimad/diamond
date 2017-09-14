import bluetooth


class Connection:
    def __init__(self, address):
        self.sock = None
        self.address = address
        self.on = True

    def connect(self):
        if self.on:
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.sock.connect((self.address, 1))

    def send_move_angle(self, angle, speed):
        if self.on:
            angle = angle / 2
            a = [chr(250), chr(angle), chr(angle), chr(250)]
            for i in a:
                self.sock.send(i)
            a = [chr(210), chr(speed), chr(speed), chr(210)]
            for i in a:
                self.sock.send(i)
    def set_zero_angle(self,angle):
        if self.on:
            angle = angle / 2
            a = [chr(200), chr(angle), chr(angle), chr(200)]
            for i in a:
                self.sock.send(i)
    def stop(self):
        if self.on:
            self.send([205, 205, 205, 205])
    def send(self, list):
        for index in range(len(list)):
            list[index] = chr(int(list[index]))
        for item in list:
            self.sock.send(item)


if __name__ == "__main__":
    c = Connection("20:16:07:05:09:55")
    print "~ Connecting ...",
    c.connect()
    print " Done !"
    while True:
        cmd = raw_input("Enter your command : ")
        if cmd == "reset":
            c.connect()
            continue
        if cmd == "":
            c.send([205, 205, 205, 205])
            continue
        if cmd == " ":
            c.send([192, 192, 192, 192])
            continue
        arr = cmd.split(" ")
        angle = int(arr[0])
        angle = angle / 2
        print "~ Sending ...",
        c.send([250, angle, angle, 250])
        c.send([210, arr[1], arr[1], 210])
        print " Done !"
