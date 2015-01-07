#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#   
#  Image lib coordinate system
#   (0,0)   i
#       -------->
#       |  
#      j|  (i,j)
#       |

'''
        Dec. 24 2014
                By simonxia
'''
import Image, redis, string, math, os
Allowed_error = 0.0001
new_len = 512
new_high = 512
new_size = (new_len,new_high)

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
        #paper's solution
        r = float(rgb[0]) / three_sum
        g = float(rgb[1]) / three_sum
        b = float(rgb[2]) / three_sum
        # change to follow the formula strictly, makes no big difference
        #r = float(rgb[0]) / 255
        #g = float(rgb[1]) / 255
        #b = float(rgb[2]) / 255

    tmp_min = min(r, g, b)
    tmp_max = max(r, g, b)
    if float_equal(tmp_max, tmp_min):
        h = 0
    elif float_equal(tmp_max, r) and g >= b:
        h = float(60*(g-b))/(tmp_max - tmp_min)
    elif float_equal(tmp_max, r) and g < b:
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
def str_to_list(string, element_type):
    no_brackets_str = string[1:len(string)-1]
    tmp_list = no_brackets_str.split(',')
    new_list = []
    if (element_type == 'int'):
        for elm in tmp_list:
            new_list.append(int(elm))
    elif (element_type == 'float'):
        for elm in tmp_list:
            new_list.append(float(elm))

    return new_list 

############
# calculate the cosine similiarity
############
def get_cos(list1, list2):
    return float(get_dot_product(list1, list2)) / (get_module(list1)*get_module(list2))

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
    

#get grey scale from RGB
def get_grey_scale(rgb):
    return rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114

#############
#calculate the inter class variance
#############
def get_inter_class_variance(list1, list2):
    return math.pow((get_avg_of_list(list1) - get_avg_of_list(list2)), 2) * len(list1) * len(list2) / math.pow((len(list1) + len(list2)), 2)

def get_avg_of_list(list_arg):
    return reduce(lambda x, y: x + y, list_arg) / len(list_arg)


#judge edge
def is_in_edge(i, j, width, height):
    if i < width/8 or i > width*7/8 or j < height/8 or j > height*7/8 :
        return True
    else:
        return False

#return 1 for <, 0 for >
def judge_front_bg(im, height, width, best, method):
    pixel_map = im.load()
    lower_height = height / 5
    upper_height = height / 5 * 4
    lower_width = width / 3
    upper_width = width / 3 * 2

    lower_count = 0
    upper_count = 0
    if method == 'hsi':
        for i in range(lower_height, upper_height):
            for j in range(lower_width, upper_width):
                tmp = quantize_hsi(rgb_to_hsi(pixel_map[i, j]))
                if tmp < best:
                    lower_count += 1
                elif tmp > best:
                    upper_count += 1
    elif method == 'hsv': #mark
        for j in range(lower_height, upper_height):
            for i in range(lower_width, upper_width):
                tmp = quantize_hsi(rgb_to_hsv(pixel_map[i, j]))
                if tmp < best:
                    lower_count += 1
                elif tmp > best:
                    upper_count += 1

    #print lower_count, upper_count
    return 0 if lower_count < upper_count else 1

#otsu method for hsv and hsi
def otsu_hsiv(im, method):
    width = im.size[0]
    height = im.size[1]
    rgb_data_list = list(im.getdata())
    pixel_total = width * height
    white_pixel = (255, 255, 255)
    quantized_data = []
    for tmp_rgb in rgb_data_list:
        if method == 'hsi':
            quantized_data.append(quantize_hsi(rgb_to_hsi(tmp_rgb)))
        elif method == 'hsv':
            quantized_data.append(quantize_hsi(rgb_to_hsv(tmp_rgb)))

    '''
    #new inplemention
    sorted_quantized_data = sorted(quantized_data) 

    diff_index_set  = []
    for tmp_index in range(len(sorted_quantized_data)):
        if tmp_index == 0:
            diff_index_set.append(tmp_index)
            continue

        if sorted_quantized_data[tmp_index - 1] != sorted_quantized_data[tmp_index]:
            diff_index_set.append(tmp_index)

    accumulated_set = []

    tmp_total = 0
    tmp_index = 1
    lenth_of_diff_index_set = len(diff_index_set)
    k = list(enumerate(sorted_quantized_data))
    for i in k:
        #print i
        if tmp_index == lenth_of_diff_index_set:
            tmp_total += i[1]
            continue

        if i[0] != diff_index_set[tmp_index]:
            tmp_total += i[1]
        else:
            accumulated_set.append(tmp_total)
            tmp_total += i[1]       #mark
            tmp_index += 1
    accumulated_set.append(tmp_total)

    accumulated_total = tmp_total

    lower_bound= min(quantized_data)
    upper_bound= max(quantized_data)
    max_inter_class_var = 0
    best= 0
    split_index = 0
    for tmp_test in range(lower_bound, upper_bound):
        for tmp_split in list(enumerate(diff_index_set)):
            if sorted_quantized_data[tmp_split[1]] == tmp_test:
                split_index = tmp_split[0]
                break
        if split_index == 0 or split_index == lenth_of_diff_index_set - 1:
            continue

        count_less = diff_index_set[split_index]
        count_greater = pixel_total - diff_index_set[split_index + 1]
        avg_less = float(accumulated_set[split_index-1]) / count_less
        avg_greater = float(accumulated_total - accumulated_set[split_index]) / count_greater 

        tmp_inter_class_val = float(math.pow(avg_greater - avg_less, 2) * count_less * count_greater) / math.pow(pixel_total, 2)
        if  tmp_inter_class_val > max_inter_class_var:
            max_inter_class_var = tmp_inter_class_val
            best = tmp_test

    '''
    #old implemention
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

    #print best

    pixel_map = im.load()
    if method == 'hsi':
        if judge_front_bg(im, height, width, best, method) == 0:
            for j in range(height):
                for i in range(width):
                    if quantize_hsi(rgb_to_hsi(pixel_map[i,j])) < best:
                        pixel_map[i, j] = white_pixel
        else:
            for j in range(height):
                for i in range(width):
                    if quantize_hsi(rgb_to_hsi(pixel_map[i,j])) > best:
                        pixel_map[i, j] = white_pixel
    elif method == 'hsv': #mark i, j
        if judge_front_bg(im, height, width, best, method) == 0:
            for j in range(height):
                for i in range(width):
                    if quantize_hsi(rgb_to_hsv(pixel_map[i, j])) < best:
                        pixel_map[i, j] = white_pixel
        else:
            for j in range(height):
                for i in range(width):
                    if quantize_hsi(rgb_to_hsv(pixel_map[i, j])) > best:
                        pixel_map[i, j] = white_pixel

    return im 


#otsu method for RGB
def otsu_rgb(im):
    width = im.size[0]
    height = im.size[1]
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

    pixel_map = im.load()
    for j in range(height):
        for i in range(width):
            if get_grey_scale(pixel_map[i, j]) >= best_grey: #to be modify, judge before paint white
                pixel_map[i, j] = white_pixel
            if is_in_edge(i, j, width, height):  #ignore the edge
                pixel_map[i, j] = white_pixel

    #crop the center part
    #tmp_crop = (64, 64, 448, 448)
    return im#.crop(tmp_crop).resize(new_size)

#here is two kinds of histogrm: percent histogram and total mount histogram
def get_color_histogram_percent(im):
    width = im.size[0] 
    height = im.size[1]
    pixel_total = width * height
    divide_level = 64
    color_dic = {}

    for i in range(4):
        for j in range(4):
            for k in range(4):
                color_dic[(i,j,k)] = 0;

    for i in range(width):
        for j in range(height):
            tmp_pixel = im.getpixel((i,j))
            color_dic[(tmp_pixel[0]/divide_level, tmp_pixel[1]/divide_level, tmp_pixel[2]/divide_level)] += 1

    result_list = []

    for i in range(4):
        for j in range(4):
            for k in range(4):
                result_list.append(float(color_dic[(i,j,k)]) / pixel_total)
    print result_list
    return result_list

#get 64RGB color histogram, divide each color channel into 4 section
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

#get accumulative histogram for 64RGB color histogram
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

#calculate color moment after otsu-hsv
def color_moment_hsv(im):
    rgb_data_list = list(im.getdata())
    hsv_data_list = []

    for i in rgb_data_list:
        hsv_data_list.append(rgb_to_hsv(i))

    miu_h = 0; miu_s = 0; miu_v = 0
    for i in hsv_data_list:
        miu_h += i[0]
        miu_s += i[1]
        miu_v += i[2]

    miu_h = float(miu_h) / (new_len * new_high)
    miu_s = float(miu_s) / (new_len * new_high)
    miu_v = float(miu_v) / (new_len * new_high)

    delta_h = 0.0; delta_s = 0.0; delta_v = 0.0
    theta_h = 0.0; theta_s = 0.0; theta_v = 0.0
    for i in hsv_data_list:
        delta_h += (i[0] - miu_h)**2
        delta_s += (i[1] - miu_s)**2
        delta_v += (i[2] - miu_v)**2
        theta_h += (i[0] - miu_h)**3
        theta_s += (i[1] - miu_s)**3
        theta_v += (i[2] - miu_v)**3

    delta_h = math.sqrt(delta_h / (new_len * new_high))
    delta_s = math.sqrt(delta_s / (new_len * new_high))
    delta_v = math.sqrt(delta_v / (new_len * new_high))

    # pow(built in) and math.pow don't support negative
    # e.g   right: -1**(1.0/3) 
    #       error: (-1)**(1.0/3) 
    #theta_h = math.pow(theta_h / (new_len * new_high), 1.0/3)
    if theta_h < 0:
        theta_h = - (- theta_h / (new_len * new_high))**(1.0/3)
    else:
        theta_h = (theta_h / (new_len * new_high))**(1.0/3)

    if theta_s < 0:
        theta_s = - (- theta_s / (new_len * new_high))**(1.0/3)
    else:
        theta_s = (theta_s / (new_len * new_high))**(1.0/3)

    if theta_v < 0:
        theta_v = - (- theta_v / (new_len * new_high))**(1.0/3)
    else:
        theta_v = (theta_v / (new_len * new_high))**(1.0/3)

    return [miu_h, miu_s, miu_v, delta_h, delta_s, delta_v, theta_h, theta_s, theta_v]

def similarity_measure_cm1_helper(a, b):
    return math.fabs(a - b) / (math.fabs(a) + math.fabs(b))

def similarity_measure_cm1(list1, list2):
    if len(list1) != len(list2) and len(list1) != 9:
        return 0

    ret = 0.0
    for i, j in zip(list1, list2):
        ret += similarity_measure_cm1_helper(i, j)

    return ret

