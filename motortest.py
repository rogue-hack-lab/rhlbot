#!/usr/bin/env python
#
# Ok, so, joystick on /dev/input/js0, use pygame to read the joystick stuff
#

import serial, sys, time

def openrobotport():
    s = serial.Serial(port="/dev/ttyS0", stopbits=2)
    return s

def getmotorremainder(m, s):
    s.write("%dQ" % m)
    #while not s.inWaiting():
    #    print "oops, serial port not ready to read yet, sleep 1..."
    #    time.sleep(0.1)
    b1 = ord(s.read())
    b2 = ord(s.read())
    v = ((b1 & 0x7f) << 7) + (b2 & 0x7f)
    print "motor:", m, "b1 b2 and v:", b1, b2, v

def getlimitswitchstatus(m, s):
    msg = "%dL" % m
    s.write(msg)
    time.sleep(0.2)
    #while not s.inWaiting():
    #    print "oops, serial port not ready to read yet, sleep 1..."
    #    time.sleep(0.1)
    b = ord(s.read())
    print "sent string '%s' to read limit switch %d gives %d '%c'" % (msg, m, b, chr(b))

if __name__ == "__main__":
    s = openrobotport()

    if not s.isOpen():
        print "ACK! can't open the serial port"
        sys.exit(1)
    for m in xrange(1, 9):
        getmotorremainder(m, s)
    for m in xrange(1, 9):
        getlimitswitchstatus(m, s)

    s.write("1M500\r")
    time.sleep(0.2)
    while s.inWaiting(): 
        s.read()
