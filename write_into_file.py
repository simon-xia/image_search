#!/usr/bin/python
'''
    write each Image's fingerprint into a file with the format of DB

                                            Jan. 5 2015
                                                    By Simon Xia

'''

import os, sys, glob, multiprocessing, Image
import color_histogram as ah
import Edge_Detect as ed

EXTS = ['jpg']

def calculate_fingerprint_one(filename):
    print filename
    #try:
    im = Image.open(filename)#.resize(ah.new_size)
    #width, height = im.size
    #except IOError:
    #    os._exit(0)

    #key = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))

    #target_part = (int(width*0.25),int(height*0.25),int(width*0.8),height)
    #key = ah.get_color_histogram_percent(ah.otsu_hsiv(im.crop(target_part), 'hsv'))
    #key = ah.get_color_histogram_percent(ed.Edge_Detect(im))
    #key = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))
    key = ah.get_color_histogram_percent(ed.Edge_Detect(ot_im))
    val = filename
    # strictly follow the protocol
    return '*3\r\n$4\r\nSADD\r\n$' + str(len(str(key))) + '\r\n' + str(key) + '\r\n$' + str(len(val)) + '\r\n' + str(val) + '\r\n'

def calculate_fingerprint_two(filename):
    print filename
    im = Image.open(filename)
    #width, height = im.size
    #center_part = (int(0.276*width),int(0.276*height),int(0.724*width),int(0.724*height))
    #center_part =  (int(width*0.25),int(height*0.25),int(width*0.8),height)
    field1_name = 'total'
    field2_name = 'center'
    #field1_val = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))
    #field2_val = ah.get_color_histogram_percent(ah.otsu_hsiv(im.crop(center_part), 'hsv'))
    #ot_im = ah.otsu_hsiv(im, 'hsv')
    ot_im = ah.otsu_hsiv(im)
    field1_val = ah.get_color_histogram_percent(ot_im)
    field2_val = ah.get_color_histogram_percent(ed.Edge_Detect(ot_im))

    return '*6\r\n$5\r\nHMSET\r\n$' + str(len(filename)) + '\r\n' + filename + '\r\n$' + str(len(field1_name)) + '\r\n' + field1_name + '\r\n$' + str(len(str(field1_val))) + '\r\n' + str(field1_val) + '\r\n$' + str(len(field2_name)) + '\r\n' + field2_name + '\r\n$' + str(len(str(field2_val))) + '\r\n' + str(field2_val) + '\r\n'
    

def write_into_file(dir_path, output_filename):
    fileHandle = open(output_filename, 'wb')  
    os.chdir(dir_path)

    images = []
    for ext in EXTS:
        images.extend(glob.glob('*.%s' % ext))

    total_cpu_count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(total_cpu_count)

    #error in task function may cause IndexError of Pool
    results_list = pool.map(calculate_fingerprint_two, images)
    #results_list = pool.map(calculate_fingerprint_one, images)

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
