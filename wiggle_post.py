from gcodeparser import GcodeParser, GcodeLine
import math


wiggle_interval = .05
angle_variation = 50



# open gcode file and store contents as variable
with open('Z:/G-Code/front_offset.ngc', 'r') as f:
    gcode = f.read()
    gcode = gcode.replace("(",";")
    gcode = gcode.replace(")","")



lines = GcodeParser(gcode).lines    # get parsed gcode lines

#Add Wiggling
length = len(lines)

i = 0
lines_added = 0

while(i<len(lines)):
    wiggle_num = 0
    if(lines[i].command == ('G', 1) and ('X' in lines[i].params.keys() or 'Y' in lines[i].params.keys())):
        if(lines[i-1].command == ('G', 1) and ('X' in lines[i-1].params.keys() or 'Y' in lines[i-1].params.keys())):
            x = lines[i].get_param('X')
            y = lines[i].get_param('Y')
            prev_x = lines[i-1].get_param('X')
            prev_y = lines[i-1].get_param('Y')
            prev_angle = lines[i-1].get_param('A')
            diff_x = x - prev_x
            diff_y = y - prev_y 

            if(diff_x != 0 or diff_y !=0):
                distance = math.dist([x,y],[prev_x,prev_y])

                wiggle_num = round(distance / wiggle_interval)

                step_x = diff_x / wiggle_num
                step_y = diff_y / wiggle_num
                c = 0
                while(c < wiggle_num):
                    lines.insert(i, GcodeLine(command=('G', 1), params={'X':round(x - step_x*c,2), 'Y':round(y - step_y*c,2), 'A':round(prev_angle-(angle_variation)/2+(c%2)*angle_variation,2),'Z': -.25, 'F':100000}, comment='Wiggle'))
                    c+=1
        
    lines_added += wiggle_num
    i+=wiggle_num
    i+=1
    print("Through line:", i)
    print("List is :",len(lines))

f_new = open('Z:/G-Code/square_wiggle.ngc','w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()


