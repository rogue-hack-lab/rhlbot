#!/usr/bin/env python

import pygame
import pygame.joystick

pygame.init()
pygame.joystick.init()

js = pygame.joystick.Joystick(0)
js.init()

print js.get_name()
print js.get_numaxes(), "axes"
print js.get_numbuttons(), "buttons"
print js.get_numhats(), "hats"

