#!/usr/bin/python

import os, sys, glob, multiprocessing, Image
import color_histogram as ah

EXTS = ['jpg']
Origin_path = os.getcwd()

#error in this function may cause IndexError of Pool
def calculate_fingerprint(filename):
    print filename
    #try:
    im = Image.open(filename)#.resize((512,512))
    #except IOError:
    #    os._exit(0)

    key = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))
    val = filename
    # strictly follow the protocol
    return '*3\r\n$4\r\nSADD\r\n$' + str(len(str(key))) + '\r\n' + str(key) + '\r\n$' + str(len(val)) + '\r\n' + str(val) + '\r\n'

def write_into_file(dir_path, output_filename):
    fileHandle = open(output_filename, 'wb')  
    os.chdir(dir_path)

    images = []
    for ext in EXTS:
        images.extend(glob.glob('*.%s' % ext))

    total_cpu_count = multiprocessing.cpu_count()

    pool = multiprocessing.Pool(total_cpu_count)

    results_list = pool.map(calculate_fingerprint, images)

    for tmp_result in results_list:
        fileHandle.write(tmp_result)  

    fileHandle.close()  

    pool.close()
    pool.join()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s <image dir>" % sys.argv[0]
    else:
        write_into_file(sys.argv[1], os.path.basename(sys.argv[1]) + '_out.txt')
