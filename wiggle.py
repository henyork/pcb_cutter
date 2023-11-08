from gcodeparser import GcodeParser, GcodeLine


distance = 10
wiggle_interval = .005
angle_variation = 16

num_wiggles = distance/wiggle_interval

lines = []


lines.append(GcodeLine(command=('G', 90), params={},comment=''))
lines.append(GcodeLine(command=('G', 1), params={'Z':1,'A':90, 'F':2000},comment='Lift'))
lines.append(GcodeLine(command=('G', 1), params={'X':0,'Y':0, 'F':2000},comment='move to origin'))
lines.append(GcodeLine(command=('G', 1), params={'Z':-.25,'F':2000},comment='drop'))
i = len(lines)
while(i < num_wiggles):
    lines.insert(i, GcodeLine(command=('G', 1), params={'Y':round(i*wiggle_interval,2),'A':90-(angle_variation)/2+(i%2)*angle_variation, 'F':80000},comment='Change angle'))
    i+=1
lines.append(GcodeLine(command=('G', 1), params={'Z':1,'A':90, 'F':2000},comment='Lift'))


f_new = open('Z:/G-Code/wiggle_line.ngc','w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()