#!/usr/bin/env python
import pygame
import scorbot

import os, sys

if __name__ == "__main__":
    r = scorbot.ERIII()
    rs = scorbot.state()

    if not r.s.isOpen():
        print "ACK! can't open the serial port"
        sys.exit(1)

    for m in xrange(1, 9):
        r.setspeed(m, 0)

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

controlthreshold = 0.2

def pygame_event_to_scorbot_state(event, state):
    if event.type == pygame.JOYBUTTONDOWN:
        if event.button == 0:
            state.modes['gripper'] = 1
        elif event.button == 2 or event.button == 3:
            state.modes['gripper'] = -1

    if event.type == pygame.JOYBUTTONUP:
        state.modes['gripper'] = 0

    if event.type == pygame.JOYAXISMOTION and event.axis == 2:
        if event.value < -1*controlthreshold:
            state.modes['base'] = 1
        elif event.value > controlthreshold:
            state.modes['base'] = -1
        else:
            state.modes['base'] = 0
            
    if event.type == pygame.JOYAXISMOTION:
        if event.axis == 1:
            if event.value < -1*controlthreshold:
                state.modes['elbow'] = -1
            elif event.value > controlthreshold:
                state.modes['elbow'] = 1
            else:
                state.modes['elbow'] = 0
        elif event.axis == 0:
            if event.value < -1*controlthreshold:
                state.modes['shoulder'] = -1
            elif event.value > controlthreshold:
                state.modes['shoulder'] = 1
            else:
                state.modes['shoulder'] = 0
                
    if event.type == pygame.JOYHATMOTION:
        if event.value[0] < 0:
            state.modes['wristroll'] = -1
        elif event.value[0] > 0:
            state.modes['wristroll'] = 1
        else:
            state.modes['wristroll'] = 0
            
        if event.value[1] < 0:
            state.modes['wristpitch'] = -1
        elif event.value[1] > 0:
            state.modes['wristpitch'] = 1
        else:
            state.modes['wristpitch'] = 0
            

# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    oldstate = rs.copy()
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
            
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 10:
                #r.save_position()
                # set "current arm state" as our go to position
                for k in scorbot.counts.keys():
                    scorbot.counts[k] = 0
            elif event.button == 11:
                # go back to last set position
                cnts = scorbot.counts.copy()
                for m in scorbot.counts.keys():
                    scorbot.counts[m] = 0
                import time
                print "have recorded motor counts of:", cnts
                for motor in cnts.keys():
                    r.stepmotor(motor, -1 * cnts[motor])
                while r.checkcompletion() == '0':
                    time.sleep(0.2)
                # r.restore_position()
                break

        pygame_event_to_scorbot_state(event, rs)
    
    r.advance(oldstate, rs)
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
