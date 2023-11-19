import proc
from copy import deepcopy

offset_list = [.35]

normal_offset_list = [.35]
normal_mill_depth_list = [-.1]
normal_angle_variation_list = [40]


mill_depth_list = [-.1]

override_depth = True

extend_length_list = [0]

wiggle_interval_list = [.01]
angle_variation_list = [18]

array_num = 1
array_interval = 5

#source_file = '../gerber/small_test_square_diag.ngc'
#source_file = '../led_test_pcb/front-reversed.ngc'
#source_file = '../led_test_pcb/front.ngc'
#source_file = '../small_test_pcb/front.ngc'
source_file = '../gerber/front.ngc'
output_dir = 'Z:/G-Code/'

base_name = proc.get_base_name(source_file)

lines = proc.load_gcode(source_file)

lines = proc.multiply(lines,array_num,array_interval)
proc.save_file(lines,output_dir,base_name,"_mult.ngc")
lines = proc.add_a(lines,mill_depth_list,extend_length_list,override_depth)
proc.save_file(lines,output_dir,base_name,"_angle.ngc")
lines = proc.add_lifts(lines,extend_length_list,mill_depth_list)   
proc.save_file(lines,output_dir,base_name,"_noffset.ngc")
normal_lines = deepcopy(lines)
lines = proc.add_offsets(lines,offset_list)
proc.save_file(lines,output_dir,base_name,"_offset.ngc")
lines = proc.add_wiggle(lines,mill_depth_list,wiggle_interval_list,angle_variation_list)
proc.save_file(lines,output_dir,base_name,"_wiggle.ngc")
normal_lines = proc.normal(normal_lines, normal_offset_list,normal_mill_depth_list, normal_angle_variation_list)
proc.save_file(normal_lines,output_dir,base_name,"_normal.ngc")
