#!/usr/bin/env python
#
# See section [Appendix-A] of the ER3-Manual.pdf for the serial command
# protocol for the arm.
#
# Ok, so, joystick on /dev/input/js0, use pygame to read the joystick stuff
#

import serial, sys, time

jointnames = ["base", "shoulder", "elbow", "wristpitch", "wristroll", "gripper"]

# the joints dict maps a joint name to a set of 
# (motor, direction) tuples which must be powered to drive 
# that joint
joints = {'base': [(1, 1)],
          'shoulder': [(2,1)],
          'elbow':    [(3,1)],
          'wristpitch': [(4,1), (5,-1)],
          'wristroll': [(4,1), (5,1)],
          'gripper': [(8,1)]}

class state:
    def __init__(self):
        # the modes dict just tells us, for a given joint, if we 
        # are going backwards (-1), not moving (0), or moving 
        # forward (+1)
        self.modes = dict(zip(jointnames, [0]*len(jointnames)))

        # counts is how many steps (total, since last reset) a given joint has moved.
        # so if you step the shoulder 5, -10, 2, -8 -> counts == -11
        self.counts = dict(zip(jointnames, [0]*len(jointnames)))

        # some constant scale factors for the motion
        self.stepmultiplier = 100
        self.grippermultiplier = 2

        # trying to use controlthreshold to reduce the twitchiness of
        # the joystick response; call it "off" unless abs(val) > controlthreshold
        self.controlthreshold = 0.2

    def copy(self):
        res = state()
        #res.joints = self.joints.copy()
        res.modes = self.modes.copy()
        res.stepmultiplier = self.stepmultiplier
        res.grippermultiplier = self.grippermultiplier
        res.controlthreshold = self.controlthreshold
        return res


def speedfromrange(r):
    speeds = [1,2,3,4,5,6,7,8,9,0]
    inx = int(round(r * len(speeds)))
    if inx >= len(speeds): inx = len(speeds)-1
    if inx < 0: inx = 0
    return speeds[inx]

counts = dict(zip(range(1,9), [0]*len(xrange(1,9))))

class ERIII:
    def __init__(self, port_="/dev/ttyS0"):
        self.s = serial.Serial(port=port_, stopbits=2)
        #self.state = scorbot.state()

    # HIGH LEVEL CONTROL #
    def save_position(self):
        for k in counts.keys():
            counts[k] = 0

    def restore_position(self):
        cnts = counts.copy()
        for m in counts.keys():
            counts[m] = 0
        print "have recorded motor counts of:", cnts, ". Returning arm to base position."
        for motor in cnts.keys():
            stepmotor(motor, -1 * cnts[motor])
        while checkcompletion() == '0':
            time.sleep(0.2)

    def advance(self, oldstate, newstate):
        # print "ERIII.advance(newstate:", newstate, ")"
        try:
            for (joint, mode) in newstate.modes.items():
                absmode = 0
                if mode < 0: absmode = -1
                elif mode > 0: absmode = 1
                speed = speedfromrange(mode)

                for (motor, direction) in joints[joint]:
                    if (mode == 0):
                        c = self.checkremainder(motor)
                        self.stopmotor(motor)
                        counts[motor] -= c
                    else:
                        #self.setspeed(motor, speedfromrange(mode))
                        steps = newstate.stepmultiplier * absmode * direction
                        counts[motor] += steps
                        self.stepmotor(motor, steps)
        except Exception, e:
            self.brake()
            for m in xrange(1, 9):
                self.stopmotor(m)
            raise e


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

    def setspeed(self, m, speed):
        """speed [1,2,3,4,5,6,7,8,9,0], 1 is slowest, 0 is fastest"""
        msg = "%dV%d" % (m, speed)
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

    # BI-directional commands
    def checkinput(self, inputinx):
        pass

    def checklimit(self, switch):
        pass

    def checkcompletion(self):
        msg = "T"
        self.s.write(msg)
        return self.s.read(1)

    def checkstatus(self):
        msg = "A"
        self.s.write(msg)
        return self.s.read(1)

    def checkremainder(self, m):
        msg = "%dQ" % m
        self.s.write(msg)
        hibyte = ord(self.s.read(1))
        lobyte = ord(self.s.read(1))
        if hibyte == 255 and lobyte == 255:
            print "ack, both bytes 0xFF, return count 0"
            return 0

        hibit = hibyte & 0b1000000
        count = ((hibyte & 0b111111)<<7) + (lobyte & 0b1111111)

        if hibit:
            count = count - 8192

        if (abs(count) > 600):
            print "checkremainder: hibyte", hibyte, "lobyte", lobyte, "count", count
        assert(abs(count) < 2000)
        return count
            
    # OTHER stuff

    def checkserial(self):
        readcount = 0
        while self.s.inWaiting():
            c = self.s.read()
            if type(c) is not type(int()):
                print "... self.s.read() returned a %s:" % type(c), c
            else:
                readcount += c
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
