#!/usr/bin/python

import os, sys, glob
import color_histogram as ah

EXTS = 'jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'

def write_into_file(dir_path, output_filename):
    fileHandle = open(output_filename, 'wb')  
    os.chdir(dir_path)
    images = []
    for ext in EXTS:
        images.extend(glob.glob('*.%s' % ext))

    count = 1
    for f in images:
        key = ah.get_color_histogram(ah.otsu_hsiv(f, 'hsv'))
        val = f
        print count, f
        # strictly follow the protocol
        tmp_str = '*3\r\n$3\r\nSET\r\n$' + str(len(str(key))) + '\r\n' + str(key) + '\r\n$' + str(len(val)) + '\r\n$' + str(val) + '\r\n'
        fileHandle.write(tmp_str)  
        count += 1

    fileHandle.close()  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s <image dir>" % sys.argv[0]
    else:
        write_into_file(sys.argv[1], os.path.basename(sys.argv[1]) + '_out.txt')
