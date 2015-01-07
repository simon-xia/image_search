#!/usr/bin/python

import Image, os
import color_histogram as ah

#image_path = './shoes_250001.jpg'
image_path = './clothes_250001.jpg'
new_len = 512
new_high = 512
new_size = (new_len,new_high)

if __name__ == '__main__':
    im = Image.open(image_path).resize(new_size)
    #ah.get_added_color_histogram(ah.get_color_histogram(ah.otsu_rgb(image_path)))
    #ah.otsu_rgb(im).show()
    ah.otsu_hsiv(im, 'hsv').show()
    ah.otsu_hsiv(im, 'hsi').show()

