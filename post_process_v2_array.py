import proc
from copy import deepcopy
import os
op_list = [("S",-0.04),("S",-.06),("S",-.08),("N",-.06,10) ,("N",-.06,30)]
#op_list = [("S",-.1)]
#op_list = [("N",-.2,80)]
preview_percentage = .08

offset_list = [.37] #.37
vertical_offset = -.04
normal_offset_list = [.37]
normal_mill_depth_list = [-.12]
normal_angle_variation_list = [80]


mill_depth_list = [-.08]

override_depth = True

extend_length_list = [0]
tool_split_line_1= "(MSG, Change tool bit to mill diameter 0.80000mm)"
tool_split_line_2= "(MSG, Change tool bit to mill diameter 0.30000mm)"
wiggle_interval_list = [.08]
angle_variation_list = [18]

array_num = 1
array_interval = 0

#source_file = '../gerber/small_test_square_diag.ngc'
#source_file = '../led_test_pcb/front-reversed.ngc'
#source_file = '../led_test_pcb/front.ngc'
#source_file = '../led_test_pcb/front.ngc'
#source_file = '../small_test_pcb/front.ngc'
#source_file = '../small_test_pcb2/front.ngc'
source_file = '../gerber/front/p2g_out/front.ngc'
#source_file = '../gerber/clear/clear_tan/p2g_out/front.ngc'
#source_file = '../stopwatch/back.ngc'
output_dir = 'Z:/nas/G-Code/'

base_name = proc.get_base_name(source_file)

lines = proc.load_gcode(source_file)





#lines = proc.split_tools(lines,tool_split_line_1, tool_split_line_2)
proc.save_file(lines,output_dir,base_name,"_split.ngc")
lines = proc.multiply(lines,array_num,array_interval)
proc.save_file(lines,output_dir,base_name,"_mult.ngc")
lines = proc.add_a(lines,mill_depth_list,extend_length_list,override_depth)
proc.save_file(lines,output_dir,base_name,"_angle.ngc")
lines = proc.add_lifts(lines,extend_length_list,mill_depth_list)   
proc.save_file(lines,output_dir,base_name,"_noffset.ngc")


full_file = os.path.join(output_dir,base_name+"_full.ngc")
full_preview_file = os.path.join(output_dir,base_name+"_preview_full.ngc")


with open(full_file, 'w') as file:
    file.close()

with open(full_preview_file, 'w') as file:
    file.close()

j = 0
for op in op_list:
    if op[0] == "S":
        straight_lines = proc.load_gcode(source_file)
        print("Straight Pass")
        mill_depth_list = [op[1]]
        straight_lines = proc.multiply(straight_lines,array_num,array_interval)
        straight_lines = proc.add_a(straight_lines,mill_depth_list,extend_length_list,override_depth)
        proc.save_file(straight_lines,output_dir,base_name,str(j)+"_angle.ngc")
        straight_lines = proc.add_lifts(straight_lines,extend_length_list,mill_depth_list)   
        proc.save_file(straight_lines,output_dir,base_name,str(j)+"_noffset.ngc")
        straight_lines = proc.add_offsets(straight_lines,offset_list)
        proc.save_file(straight_lines,output_dir,base_name,str(j)+"_offset.ngc")
        proc.append_file(straight_lines,output_dir,base_name,"_full.ngc")

        split_index = int(len(straight_lines)*preview_percentage)
        straight_preview_lines = straight_lines[:split_index]
        proc.append_file(straight_preview_lines,output_dir,base_name+"_preview","_full.ngc")

    if op[0] == "N":
        print("Normal Pass")
        normal_lines = deepcopy(lines)
        normal_preview_lines = deepcopy(lines)

        split_index = int(len(lines)*preview_percentage)
        normal_preview_lines = normal_preview_lines[:split_index]

        normal_mill_depth_list = [op[1]]
        normal_mill_angle_variation_list = [op[2]]
        normal_lines = proc.normal(normal_lines, normal_offset_list,normal_mill_depth_list, normal_angle_variation_list)
        proc.save_file(normal_lines,output_dir,base_name,str(j)+"_normal.ngc")
        proc.append_file(normal_lines,output_dir,base_name,"_full.ngc")

        normal_preview_lines = proc.normal(normal_preview_lines, normal_offset_list,normal_mill_depth_list, normal_angle_variation_list)
        proc.append_file(normal_preview_lines,output_dir,base_name+"_preview","_full.ngc")

    j+=1

#straight_lines = deepcopy(lines)
#straight_lines = proc.add_vertical_offset(straight_lines, vertical_offset,mill_depth_list)
#straight_lines = proc.save_file(straight_lines, output_dir, base_name, "_straight.ngc")


#lines = proc.add_wiggle(lines,mill_depth_list,wiggle_interval_list,angle_variation_list)
#lines = proc.add_vertical_offset(lines,vertical_offset,mill_depth_list)
#proc.save_file(lines,output_dir,base_name,"_wiggle.ngc")

#normal_lines = proc.add_vertical_offset(normal_lines, vertical_offset, normal_mill_depth_list)
#normal_lines = proc.normal(normal_lines, normal_offset_list,normal_mill_depth_list, normal_angle_variation_list)
#proc.save_file(normal_lines,output_dir,base_name,"_normal.ngc")
print("Proc Done!")


