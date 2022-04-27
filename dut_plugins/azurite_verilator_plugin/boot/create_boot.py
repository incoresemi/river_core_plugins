import shlex
import subprocess
import sys

xlen = int(sys.argv[1])
size = int(xlen/4)
width = int(xlen/8)

if xlen == 32:
    count = 8
    prefix = '''00000297
02028593
f1402573
0182a283
00028067
00000000
80000000
00000000
'''
elif xlen == 64:
    count = 4
    prefix = '''0202859300000297
0182b283f1402573
0000000000028067
0000000080000000
'''
else:
    count = 2
    prefix = '''0182b283f14025730202859300000297
00000000800000000000000000028067
'''
subprocess.run(shlex.split("dtc -O dtb -o azurite.dtb -b 0 azurite.dts"))
subprocess.run(shlex.split(f"xxd -e -c {width} azurite.dtb config.azurite"))

boothex = open('boot.hex', 'w')
boothex.write(prefix)
with open('config.azurite', 'r') as myfile:
    for line in myfile:
        count += 1
        cols = line.split()[1:-1]
        cols.reverse()
        val = f"{int(''.join(cols),16):0{size}x}"
        boothex.write(f'{val}\n')

for i in range(8192-count):
    boothex.write(''.join(['0']*size)+'\n')
boothex.close()


