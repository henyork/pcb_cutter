from gcodeparser import GcodeParser, GcodeLine
import math
import os

offset = 0.4

mill_depth = -.1
override_depth = True

extend_length = 0

wiggle_interval = .01
angle_variation = 16

source_file = '../gerber/small_test_square_diag.ngc'
output_dir = 'Z:/G-Code/'

base_name = os.path.split(source_file)[1]
base_name = base_name.split(".")[0]
print(base_name)

# open gcode file and store contents as variable
with open(source_file, 'r') as f:
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

if override_depth == True:
    for line in lines:
        if('Z' in line.params.keys()):
            if(line.params['Z']<0):
                line.params['Z'] = mill_depth
        

#Append A Values to Existing Lines

exit_flag = 0
i=0

prev_angle = 0
initial_len = len(lines)
while i<initial_len-1:
    if(lines[i].command == ('G', 1) and ('X' in lines[i].params.keys() or 'Y' in lines[i].params.keys())):
        if(lines[i+1].command == ('G', 1) and ('X' in lines[i+1].params.keys() or 'Y' in lines[i+1].params.keys())):
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
                
                while abs(prev_angle - angle) > 180:
                    #inefficency detected
                    if prev_angle > angle:
                        angle += 360
                    elif prev_angle < angle:
                        angle -= 360

                lines[i].update_param('A',round(angle,5))
                if lines[i+2].command == ('G', 4):
                    lines[i+1].update_param('A',round(angle,5))

                prev_angle = angle
        else: 
            prev_angle = 0
    else:
        prev_angle = 0

    i+=1      

i = 0
j = 0 

#Update A Values of G0 commands to match A value of next G1 move

while i<len(lines)-1:

    if lines[i].command == ('G', 0) and ('X' in lines[i].params.keys() or 'Y' in lines[i].params.keys()):
        exit_flag = False
        while i+j < len(lines)-1 and exit_flag == False:
            if(lines[i+j].command == ('G', 1) and ('X' in lines[i+j].params.keys() or 'Y' in lines[i+j].params.keys())):
                angle = lines[i+j].get_param('A')
                lines[i].update_param('A',angle)
                print("Updated a G0 on line ", i , " ", angle)
                exit_flag = True
            j+=1
        j=0
        
    i+=1      

lines_added = 0           
i=0


#Determine if adding lift between moves is nessecary

while i<initial_len+lines_added:
    
    lift_flag = False
    if lines[i].command == ('G', 1) and 'X' in lines[i].params.keys() or 'Y' in lines[i].params.keys():
        if lines[i-1].command == ('G', 1) and 'X' in lines[i-1].params.keys() or 'Y' in lines[i-1].params.keys():
            
            prev_angle= lines[i-1].get_param('A')
            angle= lines[i].get_param('A')
            

            x = lines[i].get_param('X')
            y = lines[i].get_param('Y')


            prev_x = lines[i-1].get_param('X')
            prev_y = lines[i-1].get_param('Y')

            length = math.dist((x,y),(prev_x,prev_y))
            
            x_change = x-prev_x
            y_change = y-prev_y

            x_extend = round(x_change * extend_length/length,3)
            y_extend = round(y_change * extend_length/length,3)
            
            next_x_extend = 0
            next_y_extend = 0
            if lines[i+1].command == ('G', 1) and ('X' in lines[i+1].params.keys() or 'Y' in lines[i+1].params.keys()):
                next_angle = lines[i+1].get_param('A')

                next_x = lines[i+1].get_param('X')
                next_y = lines[i+1].get_param('Y')

                next_length = math.dist((next_x,next_y),(x,y))

                next_x_change = next_x-x
                next_y_change = next_y-y

                next_x_extend = round(next_x_change * extend_length/next_length,3)
                next_y_extend = round(next_y_change * extend_length/next_length,3)

                prev_change = angle - prev_angle
                next_change = next_angle - angle
                if abs(prev_change-next_change) > 10:
                    lift_flag = True
                elif length > .5:
                    lift_flag = True
                elif lines[i+2].command == ('G', 4): 
                    lift_flag = False
                elif abs(prev_change) > 45:
                    lift_flag = True
                else:
                    lift_flag = False
                #if length < .5:
                    #lift_flag = False
            
            if lift_flag == True:
                    #insert lift + angle change
                    
                    #these go in in reverse order
                    lines[i] = GcodeLine(command=('G', 1), params={'X':x+x_extend, 'Y':y+y_extend, 'A':round(prev_angle,5)}, comment='keep prev_angle, x_extend:'+str(x_extend)+' y_extend:'+str(y_extend))
                    lines.insert(i+1, GcodeLine(command=('G', 1), params={'Z':.2, 'F':20000}, comment='Lift'))
                    lines.insert(i+2, GcodeLine(command=('G', 0), params={'A':angle}, comment='Change angle'))
                    lines.insert(i+3, GcodeLine(command=('G', 1), params={'X':x-next_x_extend, 'Y':y-next_y_extend, 'A':round(angle,5),'Z': mill_depth, 'F':20000}, comment='Drop: x_extend:'+str(next_x_extend)+' y_extend:'+str(next_y_extend)))

                    lines_added +=3

                    i+=3

    i+=1
    
# if lines[i].command == ('G', 1) and 'X' in lines[i].params.keys() or 'Y' in lines[i].params.keys():  
#     lines[i].update_param('A',round(prev_angle,5))

no_offset_file = os.path.join(output_dir,base_name+"_noffset.ngc")

f_new = open(no_offset_file,'w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()

#Add offsets

for line in lines:
    if 'X' in line.params.keys() or 'Y' in line.params.keys():
        angle = line.get_param('A')
        x = line.get_param('X')
        y = line.get_param('Y')
        x+= offset*math.cos(math.radians(angle))
        y+= offset*math.sin(math.radians(angle))
        line.update_param('X',round(x,5))
        line.update_param('Y',round(y,5))
 

offset_file = os.path.join(output_dir,base_name+"_offset.ngc")
f_new = open(offset_file,'w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()

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
                    lines.insert(i, GcodeLine(command=('G', 1), params={'X':round(x - step_x*c,2), 'Y':round(y - step_y*c,2), 'A':round(prev_angle-(angle_variation)/2+(c%2)*angle_variation,2),'Z': mill_depth, 'F':100000}, comment='Wiggle'))
                    c+=1
        
    lines_added += wiggle_num
    i+=wiggle_num
    i+=1
    print("Through line:", i)
    print("List is :",len(lines))

wiggle_file = os.path.join(output_dir,base_name+"_wiggle.ngc")
f_new = open(wiggle_file,'w')

for line in lines:
    f_new.write(line.gcode_str)
    f_new.write("\n")

f_new.close()





#print(line[1].command)
