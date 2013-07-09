#!/usr/bin/env python
import pygame
import scorbot

if __name__ == "__main__":
    r = scorbot.ERIII()

    if not r.s.isOpen():
        print "ACK! can't open the serial port"
        sys.exit(1)

    #for m in xrange(1, 9):
    #    getmotorremainder(m, s)
    #for m in xrange(1, 9):
    #    getlimitswitchstatus(m, s)

    #s.write("1M100\r")
    #time.sleep(0.2)
    #while s.inWaiting(): 
    #    s.read()
#-----------------------------------------


# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

dbmsg = ""

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputing the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def myprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10

def dumpJoystickState(tp):
    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    tp.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    tp.myprint(screen, "Debug: {}".format(dbmsg))
    tp.myprint(screen, "Number of joysticks: {}".format(joystick_count) )
    tp.indent()
    
    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
    
        tp.myprint(screen, "Joystick {}".format(i) )
        tp.indent()
    
        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        tp.myprint(screen, "Joystick name: {}".format(name) )
        
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        tp.myprint(screen, "Number of axes: {}".format(axes) )
        tp.indent()
        
        for i in range( axes ):
            axis = joystick.get_axis( i )
            tp.myprint(screen, "Axis {} value: {:>6.3f}".format(i, axis) )
        tp.unindent()
            
        buttons = joystick.get_numbuttons()
        tp.myprint(screen, "Number of buttons: {}".format(buttons) )
        tp.indent()

        for i in range( buttons ):
            button = joystick.get_button( i )
            tp.myprint(screen, "Button {:>2} value: {}".format(i,button) )
        tp.unindent()
            
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        tp.myprint(screen, "Number of hats: {}".format(hats) )
        tp.indent()

        for i in range( hats ):
            hat = joystick.get_hat( i )
            tp.myprint(screen, "Hat {} value: {}".format(i, str(hat)) )
        tp.unindent()
        
        tp.unindent()

    

pygame.init()
 
# Set the width and height of the screen [width,height]
size = [800, 500]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
    
# Get ready to print
textPrint = TextPrint()

# Stupid SDL logging bug in gamejs joystick module. Log to file
log = open("test.log", "w")

# So, each joint we control has a state: are we stepping it +, -, or leaving it alone
basemode = 0
shouldermode = 0
elbowmode = 0
wristpitchmode = 0
wristrollmode = 0
grippermode = 0

stepmultiplier = 10
grippermultiplier = 2

controlthreshold = 0.2

# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    dbmsg = ""

    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            #print>>log, str(event)
            if event.button == 0:
                grippermode = 1
            elif event.button == 2 or event.button == 3:
                grippermode = -1
            dbmsg = "BUTTONDOWN (%s) gripper %d" % (str(event), grippermode)

        if event.type == pygame.JOYBUTTONUP:
            grippermode = 0
            dbmsg = "BUTTONUP (%s) gripper %d" % (str(event), grippermode)

        if event.type == pygame.JOYAXISMOTION and event.axis == 2:
            if event.value < -1*controlthreshold:
                basemode = 1
            elif event.value > controlthreshold:
                basemode = -1
            else:
                basemode = 0
 
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                if event.value < -1*controlthreshold:
                    elbowmode = -1
                elif event.value > controlthreshold:
                    elbowmode = 1
                else:
                    elbowmode = 0
            elif event.axis == 0:
                if event.value < -1*controlthreshold:
                    shouldermode = -1
                elif event.value > controlthreshold:
                    shouldermode = 1
                else:
                    shouldermode = 0

        if event.type == pygame.JOYHATMOTION:
            #log.write(str(event))
            #log.write("\n")
            #log.write(str(event.value[0]))
            #log.write("\n")
            if event.value[0] < 0:
                wristrollmode = -1
            elif event.value[0] > 0:
                wristrollmode = 1
            else:
                wristrollmode = 0

            if event.value[1] < 0:
                wristpitchmode = -1
            elif event.value[1] > 0:
                wristpitchmode = 1
            else:
                wristpitchmode = 0

    dbmsg += ", modes(%d, %d, %d, %d, %d, %d)" % (basemode, shouldermode, elbowmode, wristpitchmode, wristrollmode, grippermode)

    if basemode != 0:
        r.stepmotor(1, (stepmultiplier * basemode))
    if shouldermode != 0:
        r.stepmotor(2, (stepmultiplier * shouldermode))
    if elbowmode != 0:
        r.stepmotor(3, (stepmultiplier * elbowmode))
    if wristpitchmode != 0:
        r.stepmotor(4, ((stepmultiplier*0.3) * wristpitchmode))
        r.stepmotor(5, (-1 * (stepmultiplier*0.3) * wristpitchmode))

    if wristrollmode != 0:
        r.stepmotor(4, ((stepmultiplier*0.3) * wristrollmode))
        r.stepmotor(5, ((stepmultiplier*0.3) * wristrollmode))

    if grippermode != 0:
        r.stepmotor(8, (grippermultiplier * grippermode))

    r.checkserial();
    # while s.inWaiting():
    #    s.read()
    dumpJoystickState(textPrint)

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick(20)

    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
