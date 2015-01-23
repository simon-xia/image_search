#!/usr/bin/python

import Image, os, glob, sys
import color_histogram as ah
#import colorhistogram108 as ah
import Edge_Detect as ed

#image_path = './shoes_245538.jpg'
#target_image_path = './clothes_250001.jpg'
#image_path = './answer/clothes_194328.jpg'
#image_path = './contest_data/clothes/clothes_image/clothes_152221.jpg'
#image_path = './contest_data/clothes/clothes_image/clothes_140160.jpg'
dir_path = './answer/shoes3'

#dir_path = '.'
#dir_path = './results'
new_len = 512
new_high = 512
new_size = (new_len,new_high)
EXTS = ['jpg']

os.chdir(dir_path)
images = []
for ext in EXTS:
    images.extend(glob.glob('*.%s' % ext))

if __name__ == '__main__':
    #width, height = im.size
    #box = (int(0.276*width),int(0.276*height),int(0.724*width),int(0.724*height))
    #ah.get_added_color_histogram(ah.get_color_histogram(ah.otsu_rgb(image_path)))
    #ah.get_hsv_color_histogram_percent(ah.otsu_rgb(im))
    #im2 = im.crop(box)
    #im2.show()
    #ah.filter_skin(im).show()
    #ah.otsu_rgb(im).show()
    #ah.otsu_hsiv(im, 'hsv').show()
    #ah.otsu_hsiv(im, 'hsi').show()

    '''
    target_im = Image.open(target_image_path)
    target_ot_im = ah.otsu_hsiv(target_im, 'hsv')
    target_e_im = ed.Edge_Detect(target_ot_im)
    target = ah.get_color_histogram_percent(target_ot_im)
    target_center = ah.get_color_histogram_percent(target_e_im)
    '''

    for image_path in images:
        im = Image.open(image_path)#.resize(new_size)
        ot_im = ah.otsu_rgb(im)
        ot_im.show()
        #ed.Edge_Detect(im).show()
        #ot_im = ah.otsu_hsiv(im, 'hsi')
        ed.Edge_Detect(ot_im).show()
        '''
        ot_im = ah.otsu_hsiv(im, 'hsv')
        #ot_im = ah.otsu_rgb(im)
        val1 = ah.get_color_histogram_percent(ot_im)
        val2 = ah.get_color_histogram_percent(e_im)
        ot_im.show()
        e_im.show()
        '''
'''
        print "****", image_path, "****"
        print "total intersecion:", ah.get_intersection_of_histogram(target, val1) 
        print "total cos:", ah.get_cos(val1, target) 
        print "center intersection:", ah.get_intersection_of_histogram(target_center, val2) 
        print "center cos:", ah.get_cos(val2, target_center)
'''

