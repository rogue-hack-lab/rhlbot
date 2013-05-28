#!/usr/bin/env python
import pygame



#-----------------------------------------
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
    

pygame.init()
 
# Set the width and height of the screen [width,height]
size = [500, 700]
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

log = open("test.log", "w")
count = 0
position = 0

# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

        if event.type == pygame.JOYAXISMOTION and event.axis == 2 and event.value != 0:
            count += 1
            position += event.value

            if (count < 1000000):
                log.write(str(event))
                log.write("\n")
                if event.value < 0:
                    s.write("1M3\r")
                else:
                    s.write("1M-3\r")
                #time.sleep(0.02)
                while s.inWaiting(): 
                    s.read()

 
        if event.type == pygame.JOYAXISMOTION and event.axis == 1 and event.value != 0:
            log.write(str(event))
            log.write("\n")
            if event.value > 0:
                s.write("3M3\r")
            else:
                s.write("3M-3\r")
            #time.sleep(0.02)
            while s.inWaiting(): 
                s.read()

    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    textPrint.myprint(screen, "Number of joysticks: {}".format(joystick_count) )
    textPrint.indent()
    
    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
    
        textPrint.myprint(screen, "Joystick {}".format(i) )
        textPrint.indent()
    
        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.myprint(screen, "Joystick name: {}".format(name) )
        
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.myprint(screen, "Number of axes: {}".format(axes) )
        textPrint.indent()
        
        for i in range( axes ):
            axis = joystick.get_axis( i )
            textPrint.myprint(screen, "Axis {} value: {:>6.3f}".format(i, axis) )
        textPrint.unindent()
            
        buttons = joystick.get_numbuttons()
        textPrint.myprint(screen, "Number of buttons: {}".format(buttons) )
        textPrint.indent()

        for i in range( buttons ):
            button = joystick.get_button( i )
            textPrint.myprint(screen, "Button {:>2} value: {}".format(i,button) )
        textPrint.unindent()
            
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        textPrint.myprint(screen, "Number of hats: {}".format(hats) )
        textPrint.indent()

        for i in range( hats ):
            hat = joystick.get_hat( i )
            textPrint.myprint(screen, "Hat {} value: {}".format(i, str(hat)) )
        textPrint.unindent()
        
        textPrint.unindent()

    
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick(20)
    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
