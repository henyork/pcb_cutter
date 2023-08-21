from gcodeparser import GcodeParser, GcodeLine
import math

# open gcode file and store contents as variable
with open('../gerber/front-truncated.ngc', 'r') as f:
    gcode = f.read()
    gcode = gcode.replace("(",";")
    gcode = gcode.replace(")","")



lines = GcodeParser(gcode).lines    # get parsed gcode lines


#Add an A paramater to each X or Y Move
for line in lines:
    if line.command == ('G',1) and ('X' in line.params.keys() or 'Y' in line.params.keys()):
        line.params['A'] = 0
    if line.command == ('G',0) and ('X' in line.params.keys() or 'Y' in line.params.keys()):
        line.params['A'] = 0

#Set A Values for each move

exit_flag = 0
i=0
lines_added = 0
prev_angle = 0
initial_len = len(lines)
while i<initial_len+lines_added-1:
    if lines[i].command == ('G', 1) and 'X' in lines[i].params.keys() or 'Y' in lines[i].params.keys():
        if lines[i+1].command == ('G', 1) and 'X' in lines[i+1].params.keys() or 'Y' in lines[i+1].params.keys():
                x1 = lines[i].get_param('X')
                y1 = lines[i].get_param('Y')
                x2 = lines[i+1].get_param('X')
                y2 = lines[i+1].get_param('Y')
                
                x3 = x2-x1
                y3 = y2-y1
                if x3 != 0:
                    angle = math.degrees(math.atan(y3/x3))
                if x3 == 0:
                    if y3 >0:
                        angle = 90
                    if y3 < 0:
                        angle = -90
                if x3 < 0:

                    if angle <= 0:
                        angle+=180
                    else:
                        angle-=180
                    
                if abs(prev_angle - angle)>20:
                    #insert lift + angle change
                    
                    #these go in in reverse order
                    lines.insert(i, GcodeLine(command=('G', 1), params={'X':x1, 'Y':y1, 'A':round(prev_angle,5)}, comment='Go to next point, but at old angle'))
                    lines.insert(i+1, GcodeLine(command=('G', 1), params={'Z':.5, 'F':8000}, comment='Lift'))
                    #lines.insert(i+2, GcodeLine(command=('G', 0), params={'A':round(angle,5)}, comment='Change angle'))
                    lines.insert(i+3, GcodeLine(command=('G', 1), params={'Z': -.1, 'F':800}, comment='Drop'))

                    lines_added +=3

                    i+=3
                if prev_angle == angle:
                    lines[i].update_param('A',round(angle,5))

                
                lines[i-1].update_param('A',round(angle,5))
                prev_angle=angle

            

    i+=1
    
if lines[i].command == ('G', 1) and 'X' in lines[i].params.keys() or 'Y' in lines[i].params.keys():  
    lines[i].update_param('A',round(prev_angle,5))


f_new = open('Z:/G-Code/no_offst_post.ngc','w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()


for line in lines:
    if 'X' in line.params.keys() or 'Y' in line.params.keys():
        angle = line.get_param('A')
        x = line.get_param('X')
        y = line.get_param('Y')
        x+= .1*math.cos(math.radians(angle))
        y+= .1*math.sin(math.radians(angle))
        line.update_param('X',round(x,5))
        line.update_param('Y',round(y,5))
        





f_new = open('Z:/G-Code/offst_post.ngc','w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()

#print(line[1].command)
