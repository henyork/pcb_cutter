import proc

offset = [0.4]

mill_depth = [-.1]
override_depth = True

extend_length = [0]

wiggle_interval = [.01]
angle_variation = [16]

source_file = '../gerber/small_test_square_diag.ngc'
output_dir = 'Z:/G-Code/'

base_name = proc.get_base_name(source_file)

lines = proc.load_gcode(source_file)
lines = proc.add_a(lines,mill_depth,extend_length,override_depth)
lines = proc.add_lifts(lines, extend_length, mill_depth)
proc.save_file(lines,output_dir,base_name,"_noffset.ngc")
lines = proc.add_offsets(lines,offset)
proc.save_file(lines,output_dir,base_name,"_offset.ngc")
lines = proc.add_wiggle(lines,mill_depth,wiggle_interval,angle_variation)
proc.save_file(lines,output_dir,base_name,"_wiggle.ngc")

