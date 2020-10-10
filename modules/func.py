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

def convert_to_html(infilename, first, last):
    # run pdftohtml https://www.xpdfreader.com/pdftohtml-man.html
    success = True
    command = "pdftohtml -q -f {} -l {} {} {}".format(first, last, infilename, PR.DIR_XPDF).split()
    pdftohtml_process = subprocess.run(command)  ## run executes command and waits for it to finish

    # signal error from pdftohtml process
    if pdftohtml_process.returncode:
        print(f"pdftohtml return code: {pdftohtml_process.returncode}")
        success = False

    # cleanup unnecessary files
    files_created = set(os.listdir(PR.DIR_XPDF))
    mask_to_remove = [".png", ".ttf", "index.html"]
    for f in files_created:
        for m in mask_to_remove:
            if m in f:
                os.remove("{}{}".format(PR.DIR_XPDF, f))

    return success

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

def ask_for_filename(args):
    infilename = None
    while True:
        infilename = input("Enter the name of pdf file:")
        if ".pdf" not in infilename and not len(infilename.split()) == 0:
            infilename += ".pdf"
        if len(infilename.split()) ==0 or (os.path.exists(infilename) and os.path.isfile(infilename)):
            break
        else:
            print(f"{infilename} does not exist.\n ")
    return infilename

def ask_for_n_pages(num):
    n = None
    ans = input("How many pages to process:")
    if ans.isdigit():
        n = int(ans)
    return n

def ask_for_starting_page():
    p = None
    ans = input(f"Enter the starting page number:")
    if ans.isdigit():
        n = int(ans)
    return n