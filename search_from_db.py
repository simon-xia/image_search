#!/usr/bin/python
'''
    Accomplish the following steps:

        1.read all data's fingerprint from DB
        2.calculate each one's score
        3.sort all in reverse order
        4.pick up top n

                                        Dec. 30 2014
                                                By Simon xia
'''

import os, sys, redis, Image
#import colorhistogram108 as ah
import color_histogram as ah
import Edge_Detect as ed

#base_dir = '/home/simon/bigdata/baidu_image/'
#base_dir = '/home/simon/bigdata/contest_data/clothes/clothes_image/'
base_dir = '/home/simon/bigdata/contest_data/shoes/shoes_image/'
results_dir = './results'
top_n = 500
db_num = 3 
weight = 6

#store in redis as Set: fingerprint as key, filename as val, the same files are collected in one set
def get_results_from_one_fingerprint():
    cos_result = {}
    i = 1
    for tmp_key in all_keyset:
        #calculate the intersection of color histogram and cosine, multiply them together as the score
        cos_result[tmp_key] = ah.get_intersection_of_histogram(target, ah.str_to_list(tmp_key, 'float')) * ah.get_cos(ah.str_to_list(tmp_key, 'float'), target)
        #cos_result[tmp_key] = float(ah.get_intersection_of_histogram(target, ah.str_to_list(tmp_key, 'int'))) / histogram_sum_target * ah.get_cos(ah.str_to_list(tmp_key, 'int'), target)

    #sort all results in reverse order by score
    sorted_cos = sorted(cos_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

   # for key, val in sorted_cos:
   #     print key, val 

    #get data from set of redis
    total_results = 0
    for tmp_key, tmp_val in sorted_cos[0:]:
        #print tmp_key, tmp_val
        tmp_set_total = r.scard(tmp_key)
        if total_results + tmp_set_total > top_n:
            while total_results <= top_n:
                #get no repeat member from set in rand order
                path = r.srandmember(tmp_key)
                print i, path
                tmp_os = 'cp '+ base_dir + path + ' ' + results_dir
                os.system(tmp_os)
                total_results += 1
                i += 1
            break
        else:
            total_results += tmp_set_total
            path_list = r.smembers(tmp_key)
            for path in path_list:
                print i, path
                tmp_os = 'cp '+ base_dir + path + ' ' + results_dir
                os.system(tmp_os)
                i += 1

#stored in redis as Hash: filename as key, total image's fingerprint as field1('total'), center part of image's fingerprint as field2('center')
def get_results_from_two_fingerprint():
    cos_result = {}
    field1_name = 'total'
    field2_name = 'center'
    for tmp_key in all_keyset:
        [val1, val2] = r.hmget(tmp_key, field1_name, field2_name)
        # calculate score1 and score2 respectively, use the method intersection of histogram and cosine
        # then, get total score: total score = score1 + 2 * score2
        cos_result[tmp_key] = ah.get_intersection_of_histogram(target, ah.str_to_list(val1, 'float')) * ah.get_cos(ah.str_to_list(val1, 'float'), target) + weight * ah.get_intersection_of_histogram(target_center, ah.str_to_list(val2, 'float')) * ah.get_cos(ah.str_to_list(val2, 'float'), target_center)

    sorted_cos = sorted(cos_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

    i = 1
    for tmp_key, tmp_val in sorted_cos[0:top_n]:
        print i, tmp_key
        os.system('cp '+ base_dir + tmp_key + ' ' + results_dir)
        i += 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s image.jpg" % sys.argv[0]
    else:
        im_path = sys.argv[1]

    im = Image.open(im_path)#.resize(ah.new_size)
    width, height = im.size
    center_part = (int(0.276*width),int(0.276*height),int(0.724*width),int(0.724*height))
    #target_part = (int(width*0.25),int(height*0.25),int(width*0.8),height)

    #target = ah.get_color_histogram(im)
    #target = ah.get_color_histogram(ah.otsu_hsiv(im, 'hsv'))
    #print target
    #target = ah.get_added_color_histogram(ah.get_color_histogram(ah.otsu_rgb(im)))

    #target = ah.get_color_histogram_percent(ah.otsu_rgb(im))
    #target_center = ah.get_color_histogram_percent(ah.otsu_rgb(im.crop(center_part)))

    #target = ah.get_color_histogram_percent(ah.filter_skin(im))
    #target_center = ah.get_color_histogram_percent(im.crop(center_part))
    #target = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))

    #target_center = ah.get_color_histogram_percent(im.crop(center_part))
    #target_center = ah.get_color_histogram_percent(ah.otsu_hsiv(im.crop(center_part), 'hsv'))
    

    #target = ah.get_hsv_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))
    #target_center = ah.get_hsv_color_histogram_percent(ah.otsu_hsiv(im.crop(center_part), 'hsv'))
    #target = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))
    #target_center = ah.get_color_histogram_percent(ah.otsu_hsiv(im.crop(center_part), 'hsv'))
    #target = ah.get_color_histogram_percent(ah.otsu_hsiv(im.crop(target_part), 'hsv'))

    #target = ah.get_color_histogram_percent(ed.Edge_Detect(im))

    #target = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsv'))

    #ot_im = ah.otsu_hsiv(im, 'hsv')
    #ot_im = ah.otsu_rgb(im)
    #target = ah.get_color_histogram_percent(ot_im)
    target = ah.get_color_histogram_percent(ed.Edge_Detect(im))
    #target_center = ah.get_color_histogram_percent(ed.Edge_Detect(ot_im))
    #ed.Edge_Detect(ot_im).show()

    histogram_sum_target = 0
    for i in target:
        histogram_sum_target += i

    r = redis.StrictRedis(host='localhost', port=6379, db=db_num)
    all_keyset = r.keys('*')

    results = {}

    os.system('rm -rf ' + results_dir)
    os.mkdir(results_dir)

    #get_results_from_two_fingerprint()
    get_results_from_one_fingerprint()
