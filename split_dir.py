#!/usr/bin/python

import os, sys

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print 'Usage %s <dir total num> <dir path>' % sys.argv[0]
else:
	dir_count = sys.argv[1]
	dir_path = '.' if len(sys.argv) < 3 else sys.argv[2]


file_postfix = '.jpg'
#total_count = os.system('ls -l ' + dir_path + ' | grep \"' + file_postfix + '$\" | wc -l')

total_count = 0
	 
for i in os.walk(dir_path):
	for j in i[2]:
		tmp = os.path.splitext(j) 
		if tmp[1] == file_postfix:
			total_count += 1

print total_count

each_total = total_count / int(dir_count)

if dir_path == '.':
	cur_path = os.getcwd()
else:
	cur_path = dir_path

each_count = 0
dir_tmp_count = 1
new_dirpath_prefix = 'split_'
tmp_new_dirpath = os.path.basename(cur_path) + '_' + new_dirpath_prefix + str(dir_tmp_count)
os.system('mkdir ' + os.path.join(dir_path, tmp_new_dirpath))
for i in os.walk(dir_path):
	#print i[0], i[1], i[2]
	if i[0] != cur_path: #ignore child dir
		break;
	for j in i[2]:
		tmp = os.path.splitext(j) 
		if tmp[1] == file_postfix:
			each_count += 1
			os.system('cp '+ i[0] + '/'+ j + ' ' + dir_path + '/' + tmp_new_dirpath)
		if each_count == each_total:
			each_count = 0
			dir_tmp_count += 1
			if dir_tmp_count <= int(dir_count):
				tmp_new_dirpath = os.path.basename(cur_path) + '_' + new_dirpath_prefix + str(dir_tmp_count)
				os.system('mkdir ' + os.path.join(dir_path, tmp_new_dirpath))
