import os
from pathlib import Path
import shutil

import subprocess
from html.parser import HTMLParser

from modules import PROJ_CONST as PR


def cleanup():
    if os.path.exists(PR.DIR_PROJECT) and os.path.isdir(PR.DIR_PROJECT):
        shutil.rmtree(PR.DIR_PROJECT)
        print("Old project flies deleted.")


def create_project():
    # create directory for the project
    Path(PR.DIR_PROJECT).mkdir(parents=False, exist_ok=True)
    Path(PR.DIR_TABULATED_CSV).mkdir(parents=False, exist_ok=True)
    Path(PR.DIR_PRODUCT_TABLES).mkdir(parents=False, exist_ok=True)


    if os.path.exists(PR.DIR_PROJECT) and os.path.isdir(PR.DIR_PROJECT):
        print(f"New project directory {PR.DIR_PROJECT} created.")
    else:
        print(f"New project directory {PR.DIR_PROJECT} creation FAILED.")


class MyHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_data_set = set()  # creates a new empty set to  hold data items from the html

    def handle_data(self, data):
        self.page_data_set.add(data)  # adds data item to the set for use in error checking algorithm

def convert_to_html(infilename):
    # run pdftohtml https://www.xpdfreader.com/pdftohtml-man.html

    command = "pdftohtml -q {} {}".format(infilename, PR.DIR_XPDF).split()
    pdftohtml_process = subprocess.run(command)  ## run executes command and waits for it to finish

    # signal error from pdftohtml process
    if pdftohtml_process.returncode:
        print(f"pdftohtml return code: {pdftohtml_process.returncode}")

def determine_n_pages(infilename):
    """determine number of pages in the infile"""
    infilename_n_pages = -1
    command = "pdfinfo {}".format(infilename)
    pdfinfo_process = subprocess.run(command, capture_output=True)

    pdfinfo_output = pdfinfo_process.stdout.decode('utf8').splitlines()
    for item in pdfinfo_output:
        if "Pages" in item:
            infilename_n_pages = item.split()[-1]
    return infilename_n_pages

