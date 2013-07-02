#!/usr/bin/env python
#
# See section [Appendix-A] of the ER3-Manual.pdf for the serial command
# protocol for the arm.
#
# Ok, so, joystick on /dev/input/js0, use pygame to read the joystick stuff
#

import serial, sys, time

class ERIII:
    def __init__(self, port_="/dev/ttyS0"):
        self.s = serial.Serial(port=port_, stopbits=2)

    def getmotorremainder(self, m):
        self.s.write("%dQ" % m)
        time.sleep(0.1) # probably not needed, self.s.read() should block
        b1 = ord(self.s.read())
        b2 = ord(self.s.read())
        v = ((b1 & 0x7f) << 7) + (b2 & 0x7f)
        print "motor:", m, "b1 b2 and v:", b1, b2, v

    def getlimitswitchstatus(self, m):
        msg = "%dL" % m
        self.s.write(msg)
        time.sleep(0.1) # probably not needed, self.s.read() should block
        b = ord(self.s.read())
        print "sent string '%s' to read limit switch %d gives %d '%c'" % (msg, m, b, chr(b))

    ### UNI directional commands: after sending, expect no response ###

    def stepmotor(self, m, stepsize):
        msg = "%dM%d\r" % (m, stepsize)
        self.s.write(msg)

    def stopmotor(self, m):
        msg = "%dP" % (m)
        self.s.write(msg)

    def brake(self):
        msg = "B"
        self.s.write(msg)

    def resume(self):
        msg = "C"
        self.s.write(msg)

    def checkserial(self):
        readcount = 0
        while self.s.inWaiting():
            readcount += self.s.read()
            print "... done, read %d bytes from serial in checkmotor" % readcount

    def domotortest(self, m, deltapos=20, deltaneg=-20):
        for delta in [deltapos, deltaneg]:
            msg = "%dM%d\r" % (m, delta)
            print "domotortest running '%s'..." % msg,
            self.s.write(msg)
            time.sleep(0.2)
            readcount = 0
            while self.s.inWaiting():
                readcount += self.s.read()
                print "... done, read %d bytes from serial in response" % readcount

if __name__ == "__main__":
    r = ERIII()

    if not r.s.isOpen():
        print "ACK! can't open the serial port"
        sys.exit(1)
    for m in xrange(1, 9):
        r.getmotorremainder(m)
    for m in xrange(1, 9):
        r.getlimitswitchstatus(m)

    # r.domotortest(1)
    r.domotortest(8)
