#!/usr/bin/python

import os, sys, redis, Image
import color_histogram as ah

base_dir = '/home/simon/bigdata/contest_data/clothes/clothes_image/'
#base_dir = '/home/simon/bigdata/contest_data/shoes/shoes_image/'
results_dir = './results'
top_n = 500

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s image.jpg" % sys.argv[0]
    else:
        im_path = sys.argv[1]

    db_num = 0
    im = Image.open(im_path).resize(ah.new_size)
    #im = Image.open(im_path)
    #target = ah.get_color_histogram(im)
    target = ah.get_color_histogram(ah.otsu_rgb(im))
    #target = ah.get_color_histogram(ah.otsu_hsiv(im, 'hsv'))
    #target = ah.get_color_histogram_percent(ah.otsu_hsiv(im, 'hsi'))
    #print target
    #target = ah.get_added_color_histogram(ah.get_color_histogram(ah.otsu_rgb(im)))

    histogram_sum_target = 0
    for i in target:
        histogram_sum_target += i

    r = redis.StrictRedis(host='localhost', port=6379, db=db_num)
    #r.set(target, im_path)
    #r.sadd(target, im_path)
    #print r.get(target)
    all_keyset = r.keys('*')

    results = {}
    cos_result = {}

    os.system('rm -rf ' + results_dir)
    os.mkdir(results_dir)

    count = 1
    for tmp_key in all_keyset:
        #print count
        cos_result[tmp_key] = ah.get_intersection_of_histogram(target, ah.str_to_list(tmp_key, 'float')) * ah.get_cos(ah.str_to_list(tmp_key, 'float'), target)
        #cos_result[tmp_key] = float(ah.get_intersection_of_histogram(target, ah.str_to_list(tmp_key, 'int'))) / histogram_sum_target * ah.get_cos(ah.str_to_list(tmp_key, 'int'), target)
        count += 1

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
                path = r.srandmember(tmp_key)
                print path
                tmp_os = 'cp '+ base_dir + path + ' ' + results_dir
                os.system(tmp_os)
                total_results += 1
            break
        else:
            total_results += tmp_set_total
            path_list = r.smembers(tmp_key)
            for path in path_list:
                print path
                tmp_os = 'cp '+ base_dir + path + ' ' + results_dir
                os.system(tmp_os)
