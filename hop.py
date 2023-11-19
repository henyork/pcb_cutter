from gcodeparser import GcodeParser, GcodeLine
import proc


#source_file = '../led_test_pcb/front.ngc'
#source_file = '../gerber/front.ngc'
output_dir = 'Z:/G-Code/hop_test/'

base_name = "hop_code"

lines = []
i=0
while i<=20:
    z = 0-i*.1/20
    lines.append(GcodeLine(command=('G', 1), params={'Z':z,'A':90, 'F':100000},comment='plunge'))
    lines.append(GcodeLine(command=('G', 1), params={'Z':z+.5*.1/20,'A':90, 'F':100000},comment='lift'))
    i+=1
lines.append(GcodeLine(command=('G', 1), params={'Z':-.1,'A':90, 'F':100000},comment='plunge'))

proc.save_file(lines,output_dir,base_name,".ngc")

