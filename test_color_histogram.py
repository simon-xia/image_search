#!/usr/bin/python

import Image, os
import color_histogram as ah

#image_path = './shoes_250001.jpg'
image_path = './clothes_122164.jpg'
new_len = 512
new_high = 512
new_size = (new_len,new_high)

if __name__ == '__main__':
    im = Image.open(image_path)#.resize(new_size)
    (width, height) = im.size
    box = (int(0.276*width),int(0.276*height),int(0.724*width),int(0.724*height))
    #ah.get_added_color_histogram(ah.get_color_histogram(ah.otsu_rgb(image_path)))
    im = im.crop(box)
    ah.otsu_rgb(im).show()
    ah.otsu_hsiv(im, 'hsv').show()
    ah.otsu_hsiv(im, 'hsi').show()

