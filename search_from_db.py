#!/usr/bin/python

import os, sys, redis, Image
import color_histogram as ah

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s image.jpg" % sys.argv[0]
    else:
        im_path = sys.argv[1]

    db_num = 0 
    target = ah.get_color_histogram(ah.otsu_rgb(im_path))
    #target = ah.get_added_color_histogram(ah.get_color_histogram(ah.otsu_rgb(im_path)))

    histogram_sum_target = 0
    for i in target:
        histogram_sum_target += i

    r = redis.StrictRedis(host='localhost', port=6379, db=db_num)
    r.set(target, im_path)
    print r.get(target)
    all_keyset = r.keys('*')

    results = {}
    cos_result = {}

    os.system('rm -rf results')
    os.mkdir('./results')

    count = 1
    for tmp_key in all_keyset:
        print count
        cos_result[tmp_key] = float(ah.get_intersection_of_histogram(target, ah.str_to_list(tmp_key))) / histogram_sum_target * ah.get_cos(ah.str_to_list(tmp_key), target)
        count += 1

    sorted_cos = sorted(cos_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

   # for key, val in sorted_cos:
   #     print key, val 

    for tmp_key, tmp_val in sorted_cos[0:50]:
        print tmp_key, tmp_val
        path = r.get(tmp_key)
        print path
        tmp_os = 'cp '+path+' ./results'
        os.system(tmp_os)

'''
        if hamming(h, int(tmp)) <= 5:
            path = r.get(tmp)
            print path
            tmp_os = 'cp '+path+' ./results'
            os.system(tmp_os)
'''
