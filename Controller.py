# Controller.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Controller module
import argparse
import sys
import os.path

variables = [["nameofvariable", "not1Dvariable"], [1, 2]]
chart_types = ["heatmap", "contour", "filled_contour", "line", "scatter"]

def get_number_of_variables(file):
    return len(file)