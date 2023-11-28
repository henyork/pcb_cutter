from os import remove
from gcodeparser import GcodeParser, GcodeLine
import math
import matplotlib.pyplot as plt 
import numpy as np


offset = .37
x_origin = 9.08797
y_origin = 7.34085

target_file = 'Z:/G-Code/spin.ngc'


gcode= "G94  ; Millimeters per minute feed rate.\nG21  ; Units == Millimeters.\nG90  ; Absolute coordinates.\nG0 S10000 ; RPM spindle speed.\nG1 F20000.0 ; Feedrate.\nG4 P0 ; dwell for no time -- G64 should not smooth over this point\nG0 Z1.0 ; retract"


lines = GcodeParser(gcode).lines
length=len(lines)
x= offset*math.cos(math.radians(0)) + x_origin
y= offset*math.sin(math.radians(0)) + y_origin
lines.insert(length,GcodeLine(command=('G', 1), params={'X':x, 'Y':y, 'A':0},comment = ""))
lines.insert(length+1,GcodeLine(command=('G', 1), params={'Z':-.08},comment = ""))
angle=0
length = len(lines)
while angle<=360:
    
    x= round(offset*math.cos(math.radians(angle)),3) + x_origin
    y= round(offset*math.sin(math.radians(angle)),3) + y_origin
    lines.insert(angle+length,GcodeLine(command=('G', 1), params={'X':x, 'Y':y, 'A':angle},comment = ""))

    angle+=1

f_new = open(target_file,'w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()