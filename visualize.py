from gcodeparser import GcodeParser, GcodeLine
import math
import matplotlib.pyplot as plt 
import numpy as np

# open gcode file and store contents as variable
with open('Z:/G-Code/no_offst_post.ngc', 'r') as f:
    gcode = f.read()
    



lines = GcodeParser(gcode).lines    # get parsed gcode lines

arrow_length = .5

initial_len = len(lines)
i = 0 
fig = plt.figure()
ax = fig.add_subplot()
while i < initial_len-1:
    if lines[i].command == ('G', 1) and 'X' in lines[i].params.keys() or 'Y' in lines[i].params.keys():
        if lines[i+1].command == ('G', 1) and 'X' in lines[i+1].params.keys() or 'Y' in lines[i+1].params.keys():
            x1 = lines[i].get_param('X')
            y1 = lines[i].get_param('Y')
            x2 = lines[i+1].get_param('X')
            y2 = lines[i+1].get_param('Y')

            x_mid = (x1+x2)/2
            y_mid = (y1+y2)/2
            
            plt.plot((x1,x2),(y1,y2),color="black",zorder=1)
            plt.text(x_mid,y_mid,str(i+1), zorder= 6)
            
            if 'A' in lines[i].params.keys() and 'A' in lines[i+1].params.keys():
                
                

                a1 = lines[i].get_param('A')
                a2 = lines[i+1].get_param('A')
                
                if(a1 != a2):
                    arrow_color = "red"
                else: 
                    arrow_color = "green"

                arrow_x1 = x_mid
                arrow_y1 = y_mid

                arrow_dx = arrow_length*math.cos(math.radians(a1))
                arrow_dy = arrow_length*math.sin(math.radians(a1))
                
                #plt.plot((arrow_x1,arrow_x2), (arrow_y1, arrow_y2), linewidth =1,color="pink")
                plt.arrow(arrow_x1,arrow_y1,arrow_dx, arrow_dy,color=arrow_color,width=.01,head_width=.2,length_includes_head=True,head_length= arrow_length, zorder=5)

    i+=1
ax.set_aspect('equal', adjustable='box')
plt.show()