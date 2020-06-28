import json
from json import JSONDecodeError
import cv2 as cv
import numpy as np
import argparse
from simple_term_menu import TerminalMenu
import os
from os import walk

class Constants:
    """Constants for this module."""
    SEPARATOR = "_"


class Cube:
    '''
class definition for a cube
https://www.w3schools.com/python/python_classes.asp
'''
    def __init__(self, cube_x, cube_y, cube_path, cube_batch):
        self.x = cube_x
        self.y = cube_y
        self.path = cube_path
        self.batch = cube_batch

class Foam_Label_Tool:

    def __init__(self):
        self.name = "cool label tool"

    def walklevel(self, some_dir, level=0):
        '''
        mod of os.walk to only get x levels deep https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
        '''
        some_dir = some_dir.rstrip(os.path.sep)
        assert os.path.isdir(some_dir)
        num_sep = some_dir.count(os.path.sep)
        for root, dirs, files in os.walk(some_dir):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs[:]

    def start(self):
        '''
        handle call arguments
        '''
        ap = argparse.ArgumentParser()
        ap.add_argument("-d", "--dataset", default="/home/jonaszagatta/gitprojects/datasets/foam/", help="path to input dataset (folder) with subfolders for all foam batches")
        ap.add_argument("-g", "--gamma", type=bool, default=False, help="do you want to use the gamma images?")
        args = vars(ap.parse_args())

        '''
        get all folders in dataset for selection
        based on https://www.tutorialspoint.com/python/os_walk.htm + walklevel
        initialize array and append: https://www.geeksforgeeks.org/python-which-is-faster-to-initialize-lists/
        '''
        foam_dir = []
        foam_name = []
        for root, dirs, files in self.walklevel(args["dataset"]):
            for name in dirs:
                foam_dir.append(os.path.join(root, name))
                foam_name.append(name)


        '''
        show menu to select batch 
        from https://stackoverflow.com/questions/45022566/create-python-cli-with-select-interface
        '''
        print("select the foam you want to label")
        terminal_menu = TerminalMenu(foam_name)
        choice_index = terminal_menu.show()
        print(foam_dir[choice_index])

        cubes = []
        for root, dirs, files in self.walklevel(foam_dir[choice_index]):
            for name in files:
                '''
                filename convention:
                image_<x>_<y>_<side>_orig_<bit>.png

                example

                os.path.join(root, name)
                '''
                
                #split filename to get cubes position
                '''
                name.split("_")

                a_cube = Cube(<x>, <y>, os.path.join(root, name), foam_name[choice_index])
                cubes.append(a_cube)
                '''
                print(os.path.join(root, name))

if __name__ == '__main__':
    labeltool = Foam_Label_Tool()
    labeltool.start()