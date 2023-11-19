from gcodeparser import GcodeParser, GcodeLine
import proc


#source_file = '../led_test_pcb/front.ngc'
#source_file = '../gerber/front.ngc'
output_dir = 'Z:/G-Code/vertical_wiggle_test/'

base_name = "vertical_wiggle_code"

lines = []
i=0
while i<=40:
    lines.append(GcodeLine(command=('G', 1), params={'Z':round(.1-.005*i,5),'A':90-(8/2)+(i%2)*8, 'F':100000},comment='plunge'))
    i+=1


proc.save_file(lines,output_dir,base_name,".ngc")

