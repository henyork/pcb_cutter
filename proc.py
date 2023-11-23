from gcodeparser import GcodeParser, GcodeLine
import math
import os
from copy import deepcopy

def get_base_name(source_file):
    base_name = os.path.split(source_file)[1]
    base_name = base_name.split(".")[0]
    return base_name

def load_gcode(source_file):
    # open gcode file and store contents as variable
    with open(source_file, 'r') as f:
        gcode = f.read()
        gcode = gcode.replace("(",";")
        gcode = gcode.replace(")","")
    lines = GcodeParser(gcode).lines    # get parsed gcode lines
    return lines

def add_a(lines, mill_depth_list, extend_length_list, override_depth):

    #Add an A paramater to each X or Y Move
    for line in lines:
        if line.command == ('G',1) and ('X' in line.params.keys() or 'Y' in line.params.keys()):
            line.params['A'] = 0
        if line.command == ('G',0) and ('X' in line.params.keys() or 'Y' in line.params.keys()):
            line.params['A'] = 0

    if override_depth == True:
        mill_depth = mill_depth_list[0]
        for line in lines:
            if line.comment != None:
                    try:
                        rep_num = int(line.comment)
                        try:
                            mill_depth = mill_depth_list[rep_num]
                        except IndexError:
                            pass
                    except ValueError:
                        pass
                   
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
    return lines

def add_lifts(lines, extend_length_list, mill_depth_list):
    i=0
    lines_added = 0
    #Determine if adding lift between moves is nessecary
    extend_length = extend_length_list[0]
    mill_depth = mill_depth_list[0]
    initial_len = len(lines)
    while i<initial_len+lines_added:
        
        lift_flag = False
        if lines[i].command == ('G', 1) and 'X' in lines[i].params.keys() or 'Y' in lines[i].params.keys():
            if lines[i-1].command == ('G', 1) and 'X' in lines[i-1].params.keys() or 'Y' in lines[i-1].params.keys():
                if lines[i].comment != None:
                    rep_num = int(lines[i].comment)
                    try:
                        extend_length = extend_length_list[rep_num]
                    except IndexError:
                        pass
                    try:
                         mill_depth = mill_depth_list[0]
                    except IndexError:
                        pass
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

                    
                    next_change = next_angle - angle
                    if lines[i].get_param('X') == 5.39722:
                        print("break")
                prev_change = angle - prev_angle
                z_lift = .2
                twist_flag = False
                comment = lines[i].comment
                if lines[i+1].command == ('G', 4):
                    lift_flag = False
                    print('Skip bc G4')
                if abs(prev_change) > 20: 
                    lift_flag = True
                    if abs(prev_change) < 91:
                        twist_flag = True
                else:
                    lift_flag = False
                

                
                if lift_flag == True and twist_flag == False:
                        #insert lift + angle change
                        
                        
                        lines[i] = GcodeLine(command=('G', 1), params={'X':x+x_extend, 'Y':y+y_extend, 'A':round(prev_angle,5)},comment = comment)
                        lines.insert(i+1, GcodeLine(command=('G', 1), params={'Z':z_lift, 'F':20000},comment = comment))
                        lines.insert(i+2, GcodeLine(command=('G', 0), params={'A':angle},comment = comment))
                        lines.insert(i+3, GcodeLine(command=('G', 1), params={'X':x-next_x_extend, 'Y':y-next_y_extend, 'A':round(angle,5),'Z': mill_depth, 'F':20000},comment = comment))

                        lines_added +=3

                        i+=3
                if lift_flag == True and twist_flag == True:
                        #insert lift + angle change
                        
                        
                        lines[i] = GcodeLine(command=('G', 1), params={'X':x+x_extend, 'Y':y+y_extend, 'A':round(prev_angle,5)},comment = comment)
                        lines.insert(i+1, GcodeLine(command=('G', 1), params={'X':x-next_x_extend, 'Y':y-next_y_extend, 'A':round(angle,5),'Z': mill_depth, 'F':20000},comment = comment))

                        lines_added +=1

                        i+=1

        i+=1
    return lines   


def add_offsets(lines, offset_list):
    offset = offset_list[0]
    #Add offsets

    for line in lines:

        if line.comment != None:
            try:
                rep_num = int(line.comment)
                try:
                    offset = offset_list[rep_num]
                except IndexError:
                        pass
            except ValueError:
                pass
            
        if 'X' in line.params.keys() or 'Y' in line.params.keys():
            angle = line.get_param('A')
            x = line.get_param('X')
            y = line.get_param('Y')
            x+= offset*math.cos(math.radians(angle))
            y+= offset*math.sin(math.radians(angle))
            line.update_param('X',round(x,5))
            line.update_param('Y',round(y,5))
    return lines
 
def add_wiggle(lines,mill_depth_list, wiggle_interval_list, angle_variation_list):
    #Add Wiggling

    i = 0
    lines_added = 0
    mill_depth = mill_depth_list[0]
    wiggle_interval = wiggle_interval_list[0]
    angle_variation = angle_variation_list[0]
    while(i<len(lines)):
        wiggle_num = 0
        if(lines[i].command == ('G', 1) and ('X' in lines[i].params.keys() or 'Y' in lines[i].params.keys())):
            if(lines[i-1].command == ('G', 1) and ('X' in lines[i-1].params.keys() or 'Y' in lines[i-1].params.keys())):
                x = lines[i].get_param('X')
                y = lines[i].get_param('Y')
                angle = lines[i].get_param('A')
                comment = lines[i].comment
                if lines[i].comment != None:
                    rep_num = int(lines[i].comment)
                    try:
                        mill_depth = mill_depth_list[rep_num]
                    except IndexError:
                        pass
                    try:
                        angle_variation = angle_variation_list[rep_num]
                    except IndexError:
                        pass
                    try:
                        wiggle_interval = wiggle_interval_list[rep_num]
                    except IndexError:
                        pass

                prev_x = lines[i-1].get_param('X')
                prev_y = lines[i-1].get_param('Y')
                prev_angle = lines[i-1].get_param('A')
                diff_x = x - prev_x
                diff_y = y - prev_y
                diff_a = angle - prev_angle
                if(diff_x != 0 or diff_y !=0):
                    distance = math.dist([x,y],[prev_x,prev_y])
                    
                    wiggle_num = round(distance / wiggle_interval)
                    if(wiggle_num == 0):
                        wiggle_num = 1

                    step_x = diff_x / wiggle_num
                    step_y = diff_y / wiggle_num
                    c = 0
                    
                    step_a = diff_a / wiggle_num
                    while(c < wiggle_num):
                        lines.insert(i, GcodeLine(command=('G', 1), params={'X':round(x - step_x*c,2), 'Y':round(y - step_y*c,2), 'A':round(angle-step_a*c-(angle_variation)/2+(c%2)*angle_variation,2), 'F':100000},comment = comment))
                        c+=1

        
        lines_added += wiggle_num
        i+=wiggle_num
        i+=1
        print("Through line:", i)
        print("List is :",len(lines))
    return lines



def save_file(lines, output_dir, base_name, string):


    no_offset_file = os.path.join(output_dir,base_name+string)

    f_new = open(no_offset_file,'w')

    for line in lines:
        f_new.write(line.gcode_str)
        f_new.write("\n")

    f_new.close()

def multiply(lines, count, interval):
    i = 0
    cut_line = 0
    while i < len(lines) and cut_line == 0:
        if lines[i].command == ('M', 0):
            cut_line = i
        i+=1
    i=0
    while i < len(lines) and cut_line == 0:
        if lines[i].command == ('G', 90):
            cut_line = i
        i+=1
    start_lines = lines[:cut_line]
    rep_lines = lines[cut_line+1:]

    new_lines = []
    i = 0 
    while i<count:
        if(i == 1):
            print("breakpoint reached")
            
        for line in rep_lines:
            new_line = deepcopy(line)
            if 'X' in line.params.keys():
                x = line.get_param('X')
                new_line.params['X'] = x + interval*i
                new_line.comment = str(i)
            new_lines.append(deepcopy(new_line))
        i+=1
    return start_lines+new_lines
        
def normal(lines, normal_offset_list, normal_mill_depth_list, normal_angle_variation_list):
    normal_offset = normal_offset_list[0]
    normal_offset = normal_mill_depth_list[0]
    normal_offset = normal_angle_variation_list[0]
    #Add offsets

    for line in lines:

        if line.comment != None:
            try:
                rep_num = int(line.comment)
                try:
                    normal_offset = normal_offset_list[rep_num]
                except IndexError:
                        pass
                try:
                    normal_mill_depth = normal_mill_depth_list[rep_num]
                except IndexError:
                        pass
                try:
                    normal_angle_variation = normal_angle_variation_list[rep_num]
                except IndexError:
                        pass
            except ValueError:
                pass

    side1 = deepcopy(lines)
    side2 = deepcopy(lines)
    i=0
    while i < len(lines):
        if 'A' in lines[i].params.keys():
            a = lines[i].get_param('A')
            side1[i].params['A'] = a + .5*normal_angle_variation
            side2[i].params['A'] = a - .5*normal_angle_variation
        if 'Z' in lines[i].params.keys():
            z = lines[i].get_param('Z')
            if(z < 0):
                side1[i].params['Z'] = normal_mill_depth
                side2[i].params['Z'] = normal_mill_depth
        if lines[i].command == ('M', 2):
            
            side1.pop(i)
            side2.pop(i)
            print(i)
              

        i+=1
    i=0
    print(normal_offset)
    while i<len(lines):
        if 'X' in lines[i].params.keys() or 'Y' in lines[i].params.keys():
            a1 = side1[i].get_param('A')
            a2 = side2[i].get_param('A')
            x1 = lines[i].get_param('X')
            y1 = lines[i].get_param('Y')
            x2 = lines[i].get_param('X')
            y2 = lines[i].get_param('Y')
            x1+= normal_offset*math.cos(math.radians(a1))
            y1+= normal_offset*math.sin(math.radians(a1))
            x2+= normal_offset*math.cos(math.radians(a2))
            y2+= normal_offset*math.sin(math.radians(a2))
            side1[i].params['X'] = round(x1,2)
            side1[i].params['Y'] = round(y1,2)
            side2[i].params['X'] = round(x2,2)
            side2[i].params['Y'] = round(y2,2)
        i+=1
    return side1+side2