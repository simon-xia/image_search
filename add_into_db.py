#!/usr/bin/python

import redis, sys, os, glob
import color_histogram as ah

EXTS = 'jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'

def add_into_db(db_fd, dir_path):
    os.chdir(dir_path)
    images = []
    for ext in EXTS:
        images.extend(glob.glob('*.%s' % ext))

    count = 1
    for f in images:
        #db_fd.set(get_color_histogram(otsu_rgb(f)), dir_path+'/'+f)
        #key = ah.color_moment_hsv(ah.otsu_rgb(f))
        key = ah.get_color_histogram(ah.otsu_hsiv(f, 'hsv'))
        db_fd.set(key, dir_path+'/'+f)
        print count, key, f
        count += 1
        #db_fd.set(get_added_color_histogram(get_color_histogram(otsu_rgb(f))), dir_path+'/'+f)


if __name__ == '__main__':
    db_num = 3
    if len(sys.argv) != 2:
        print "Usage: %s <image dir>" % sys.argv[0]
    else:
        r = redis.StrictRedis(host='localhost', port=6379, db=db_num)
        add_into_db(r, sys.argv[1])
