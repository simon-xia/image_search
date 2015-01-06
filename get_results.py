#!/usr/bin/python

import os, fileinput

path = '/home/simon/bigdata/contest_data/clothes/clothes_image/'
des_dir = './tmp_results'
#os.system('mkdir ' + des_dir)

if __name__ == "__main__":
    for line in fileinput.input("rrr.txt"):
        tmp = 'cp ' + path + line[:-1] + ' ./tmp_results'
        print tmp
        os.system(tmp)

