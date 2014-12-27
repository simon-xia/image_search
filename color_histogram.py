#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
        Dec. 24 2014
                By simonxia
'''
import Image, redis, string, math, os, glob, sys
EXTS = 'jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'
image_path = './clothes_250001.jpg'
#image_path = '/home/simon/Pictures/DSC00587.JPG'
Allowed_error = 0.0001
new_len = 512
new_high = 512
new_size = (new_len,new_high)
im = Image.open(image_path).resize(new_size)

def float_equal(f1, f2):
    return math.fabs(f1-f2) <= Allowed_error
    
def rgb_to_hsv(rgb):
    '''
    r = 0 if rgb[0] == 0 else float(rgb[0]) / (rgb[0]+rgb[1]+rgb[2])
    g = 0 if rgb[1] == 0 else float(rgb[1]) / (rgb[0]+rgb[1]+rgb[2])
    b = 0 if rgb[2] == 0 else float(rgb[2]) / (rgb[0]+rgb[1]+rgb[2])
    '''
    three_sum = rgb[0]+rgb[1]+rgb[2]
    if three_sum == 0:
        r = g = b = 1.0/3   #mark
    else:
        r = float(rgb[0]) / three_sum
        g = float(rgb[1]) / three_sum
        b = float(rgb[2]) / three_sum

    tmp_min = min(r, g, b)
    tmp_max = max(r, g, b)
    if float_equal(tmp_max, tmp_min):
        h = 0
    elif float_equal(tmp_max, r) and int(g) >= int(b):
        h = float(60*(g-b))/(tmp_max - tmp_min)
    elif float_equal(tmp_max, r) and int(g) < int(b):
        h = float(60*(g-b))/(tmp_max - tmp_min) + 360
    elif float_equal(tmp_max, g):
        h = float(60*(b-r))/(tmp_max - tmp_min) + 120
    elif float_equal(tmp_max, b):
        h = float(60*(r-g))/(tmp_max - tmp_min) + 240

    s = 0 if float_equal(tmp_max, 0) else float(tmp_max - tmp_min)/tmp_max
    v = tmp_max
    #print h, s, v
    return [h, s, v]

def rgb_to_hsi(rgb):
    # normalize RGB into [0,1]
    #r = float(rgb[0])/255; g = float(rgb[1])/255; b = float(rgb[2])/255
    r = 0 if rgb[0] == 0 else float(rgb[0]) / (rgb[0]+rgb[1]+rgb[2])
    g = 0 if rgb[1] == 0 else float(rgb[1]) / (rgb[0]+rgb[1]+rgb[2])
    b = 0 if rgb[2] == 0 else float(rgb[2]) / (rgb[0]+rgb[1]+rgb[2])

    if rgb[2] == 0:
        b = 0
    else:
        b = (float(rgb[0]))/(rgb[0]+rgb[1]+rgb[2])

    a = min(r,g,b)
    i = float(r+b+g)/3
    if a == 0:
        s = 1
    else:
        s = 1 - float(3*a)/(r+g+b)
    if r == g or r == b:
        theta = 90
    else:
        theta = (180.0/math.pi)*math.acos((((r-g)+(r-b))/2.0)/math.sqrt(math.pow((r-g), 2)+(r-b)*(g-b)))

    if b > g:
        theta = 360 - theta
    #print theta, s, i
    return [theta, s, i]

# eggache
def quantize_hsi_helper(s):
    if s >= 0 and  s <= 0.2:
        s = 0
    elif s > 0.2 and s <= 0.7:
        s = 1
    elif s > 0.7 and s <= 1:
        s = 2
    return s

def quantize_hsi(hsi):
    h = int(hsi[0])
    if h <= 20 or h >= 316:
        h = 0
    elif h >= 21 and h <= 40:
        h = 1
    elif h >= 41 and h <= 75:
        h = 2
    elif h >= 76 and h <= 155:
        h = 3
    elif h >= 156 and h <= 190:
        h = 4
    elif h >= 191 and h <= 270:
        h = 5
    elif h >= 271 and h <= 295:
        h = 6
    elif h >= 296 and h <= 315:
        h = 7

    s = quantize_hsi_helper(hsi[1])
    i = quantize_hsi_helper(hsi[2])

    #print h, s, i
    return 9*h + 3*s + i
    

#turn string '[111,112,...119]' into a list
def str_to_list(string):
    no_brackets_str = string[1:len(string)-2]
    tmp_list = no_brackets_str.split(',')
    new_list = []
    for elm in tmp_list:
        new_list.append(int(elm))

    return new_list 

def get_dot_product(list1, list2):
    lenth = len(list1)
    result = 0
    for i in range(lenth):
        result += list1[i]*list2[i]
    return result

def get_module(arg_list):
    result = 0.0
    for i in range(len(arg_list)):
        result += math.pow(arg_list[i],2)
    return math.sqrt(result)
    
def get_cos(list1, list2):
    return float(get_dot_product(list1, list2)) / (get_module(list1)*get_module(list2))

#get grey scale from RGB
def get_grey_scale(rgb):
    return rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114

def get_avg_of_list(list_arg):
    return reduce(lambda x, y: x + y, list_arg) / len(list_arg)

def get_inter_class_variance(list1, list2):
    return math.pow((get_avg_of_list(list1) - get_avg_of_list(list2)), 2) * len(list1) * len(list2) / math.pow((len(list1) + len(list2)), 2)

def is_in_edge(i, j):
    edge_len = new_high/8
    if i < edge_len or i > edge_len*7 or j < edge_len or j > edge_len*7:
        return True
    else:
        return False

#return 1 for <, 0 for >
def judge_front_bg(im, height, width, best, method):
    lower_height = height / 5
    upper_height = height / 5 * 4
    lower_width = width / 3
    upper_width = width / 3 * 2

    lower_count = 0
    upper_count = 0
    if method == 'hsi':
        for i in range(lower_height, upper_height):
            for j in range(lower_width, upper_width):
                tmp = quantize_hsi(rgb_to_hsi(im.getpixel((i, j))))
                if tmp < best:
                    lower_count += 1
                elif tmp > best:
                    upper_count += 1
    elif method == 'hsv':
        for i in range(lower_height, upper_height):
            for j in range(lower_width, upper_width):
                tmp = quantize_hsi(rgb_to_hsv(im.getpixel((i, j))))
                if tmp < best:
                    lower_count += 1
                elif tmp > best:
                    upper_count += 1

    return 0 if lower_count < upper_count else 1



def otsu_hsiv(image_path, method):
    im = Image.open(image_path).resize(new_size)
    rgb_data_list = list(im.getdata())
    white_pixel = (255, 255, 255)
    quantized_data = []
    for tmp_rgb in rgb_data_list:
        if method == 'hsi':
            quantized_data.append(quantize_hsi(rgb_to_hsi(tmp_rgb)))
        elif method == 'hsv':
            quantized_data.append(quantize_hsi(rgb_to_hsv(tmp_rgb)))

    max_inter_class_var = 0
    best= 0
    lower_bound= min(quantized_data)
    upper_bound= max(quantized_data)
    #print lower_bound, upper_bound
    for tmp_test in range(int(lower_bound), int(upper_bound)):
        #print "try %d ..." %(tmp_test)
        less_list = [] 
        greater_list = []

        for tmp_quantized_data in quantized_data:
            if tmp_test < tmp_quantized_data:
                less_list.append(tmp_quantized_data)
            else:
                greater_list.append(tmp_quantized_data)

        if (len(greater_list) == 0 or len(less_list) == 0):
            continue

        tmp_inter_class_val = get_inter_class_variance(less_list, greater_list)   
        if  tmp_inter_class_val > max_inter_class_var:
            max_inter_class_var = tmp_inter_class_val
            best = tmp_test

    print best

    if method == 'hsi':
        if judge_front_bg(im, new_high, new_len, best, method) == 1:
            for i in range(new_high):
                for j in range(new_len):
                    if quantize_hsi(rgb_to_hsi(im.getpixel((i,j)))) < best:
                        im.putpixel((i, j), white_pixel)
        else:
            for i in range(new_high):
                for j in range(new_len):
                    if quantize_hsi(rgb_to_hsi(im.getpixel((i,j)))) > best:
                        im.putpixel((i, j), white_pixel)
    elif method == 'hsv':
        for i in range(new_high):
            for j in range(new_len):
                if quantize_hsi(rgb_to_hsv(im.getpixel((i,j)))) < best:
                    im.putpixel((i, j), white_pixel)
        '''
        if judge_front_bg(im, new_high, new_len, best, method) == 1:
            for i in range(new_high):
                for j in range(new_len):
                    if quantize_hsi(rgb_to_hsv(im.getpixel((i,j)))) < best:
                        im.putpixel((i, j), white_pixel)
        else:
            for i in range(new_high):
                for j in range(new_len):
                    if quantize_hsi(rgb_to_hsv(im.getpixel((i,j)))) > best:
                        im.putpixel((i, j), white_pixel)
'''
    return im 


def otsu_rgb(image_path):
    im = Image.open(image_path).resize(new_size)
    rgb_data_list = list(im.getdata())
    white_pixel = (255, 255, 255)
    grey_data = []
    for tmp_rgb in rgb_data_list:
        grey_data.append(get_grey_scale(tmp_rgb))

    max_inter_class_var = 0
    best_grey = 0
    lower_bound_grey = min(grey_data)
    upper_bound_grey = max(grey_data)
    for tmp_grey_test in range(int(lower_bound_grey), int(upper_bound_grey)):
        less_list = [] 
        greater_list = []

        for tmp_grey_data in grey_data:
            if tmp_grey_test < tmp_grey_data:
                less_list.append(tmp_grey_data)
            else:
                greater_list.append(tmp_grey_data)

        if (len(greater_list) == 0 or len(less_list) == 0):
            continue

        tmp_inter_class_val = get_inter_class_variance(less_list, greater_list)   
        if  tmp_inter_class_val > max_inter_class_var:
            max_inter_class_var = tmp_inter_class_val
            best_grey = tmp_grey_test

    #print best_grey

    for i in range(new_high):
        for j in range(new_len):
            if get_grey_scale(im.getpixel((i,j))) >= best_grey:
                im.putpixel((i, j), white_pixel)
            if is_in_edge(i, j):  #ignore the edge
                im.putpixel((i, j), white_pixel)

    return im 


def get_color_histogram(im):
    divide_level = 64
    color_dic = {}

    for i in range(4):
        for j in range(4):
            for k in range(4):
                color_dic[(i,j,k)] = 0;

    for i in range(new_len):
        for j in range(new_high):
            tmp_pixel = im.getpixel((i,j))
            color_dic[(tmp_pixel[0]/divide_level, tmp_pixel[1]/divide_level, tmp_pixel[2]/divide_level)] += 1

    result_list = []

    for i in range(4):
        for j in range(4):
            for k in range(4):
                result_list.append(color_dic[(i,j,k)])

    #print result_list
    return result_list

def get_added_color_histogram(color_list):
    added_list = []
    i = 0
    for j in range(8, 65, 8):
        added_list.append(reduce(lambda x, y: x + y, color_list[i:j]))
        i = j

    #print added_list
    return added_list

def get_intersection_of_histogram(list1, list2):
    tmp_sum = 0
    if len(list1) != len(list2):
        return 0
    for i in range(64):
        tmp_sum += list1[i] if list1[i] < list2[i] else list2[i]
    return tmp_sum

def add_into_db(db_fd, dir_path):
    os.chdir(dir_path)
    images = []
    for ext in EXTS:
        images.extend(glob.glob('*.%s' % ext))

    count = 1
    for f in images:
        print count, f
        db_fd.set(get_color_histogram(otsu_rgb(f)), dir_path+'/'+f)
        count += 1
        #db_fd.set(get_added_color_histogram(get_color_histogram(otsu_rgb(f))), dir_path+'/'+f)


'''

if __name__ == '__main__':
    db_num = 1
    if len(sys.argv) != 2:
        print "Usage: %s <image dir>" % sys.argv[0]
    else:
        r = redis.StrictRedis(host='localhost', port=6379, db=db_num)
        add_into_db(r, sys.argv[1])
'''
#get_added_color_histogram(get_color_histogram(otsu_rgb(image_path)))
otsu_rgb(image_path).show()
otsu_hsiv(image_path, 'hsv').show()
otsu_hsiv(image_path, 'hsi').show()

