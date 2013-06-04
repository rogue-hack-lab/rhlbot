#!/usr/bin/env python
#
# See section [Appendix-A] of the ER3-Manual.pdf for the serial command
# protocol for the arm.
#
# Ok, so, joystick on /dev/input/js0, use pygame to read the joystick stuff
#

import serial, sys, time

def openrobotport():
    s = serial.Serial(port="/dev/ttyS0", stopbits=2)
    return s

def getmotorremainder(m, s):
    s.write("%dQ" % m)
    time.sleep(0.1) # probably not needed, s.read() should block
    b1 = ord(s.read())
    b2 = ord(s.read())
    v = ((b1 & 0x7f) << 7) + (b2 & 0x7f)
    print "motor:", m, "b1 b2 and v:", b1, b2, v

def getlimitswitchstatus(m, s):
    msg = "%dL" % m
    s.write(msg)
    time.sleep(0.1) # probably not needed, s.read() should block
    b = ord(s.read())
    print "sent string '%s' to read limit switch %d gives %d '%c'" % (msg, m, b, chr(b))

def domotortest(m, s, deltapos=20, deltaneg=-20):
    for delta in [deltapos, deltaneg]:
        msg = "%dM%d\r" % (m, delta)
        print "domotortest running '%s'..." % msg,
        s.write(msg)
        time.sleep(0.2)
        readcount = 0
        while s.inWaiting():
            readcount += s.read()
        print "... done, read %d bytes from serial in response" % readcount


if __name__ == "__main__":
    s = openrobotport()

    if not s.isOpen():
        print "ACK! can't open the serial port"
        sys.exit(1)
    for m in xrange(1, 9):
        getmotorremainder(m, s)
    for m in xrange(1, 9):
        getlimitswitchstatus(m, s)

    # domotortest(1, s)
    domotortest(8, s)
