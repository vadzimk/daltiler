import os
from pathlib import Path
import shutil

import subprocess
from html.parser import HTMLParser

from modules import PROJ_CONST as PR


def cleanup():
    if os.path.exists(PR.DIR_PROJECT) and os.path.isdir(PR.DIR_PROJECT):
        print("Deleting old project flies...")
        shutil.rmtree(PR.DIR_PROJECT)

    if os.path.exists("xpdf") and os.path.isdir("xpdf"):
        print("xpdf exists, deleting it....")
        shutil.rmtree("xpdf")


def create_project():
    print("Creating new project directory")
    # create directory for the project
    Path(PR.DIR_PROJECT).mkdir(parents=False, exist_ok=True)
    Path(PR.DIR_TABULATED_CSV).mkdir(parents=False, exist_ok=True)
    Path(PR.DIR_PRODUCT_TABLES).mkdir(parents=False, exist_ok=True)


class MyHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_data_set = set()  # creates a new empty set to  hold data items from the html

    def handle_data(self, data):
        self.page_data_set.add(data)  # adds data item to the set for use in error checking algorithm

