import os
from corcym.settings import PATH_P


path = PATH_P
files = os.listdir(path)

if files:
	for f in files:
		rm_path = PATH_P+f'{f}'
		os.remove(rm_path)
