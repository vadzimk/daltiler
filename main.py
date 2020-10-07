import shutil
import sys  # access to functions and variables that allow for working with Python interpreter
from classes import *
from pathlib import Path
import os

import PROJ_CONST as PR



args = sys.argv  # get the list of arguments

infilename = args[1] if len(args) == 2 else 'test1.pdf'  # infilename is the args[1] or default to 'test1.pdf'

print(f"Working on {infilename}\nPlease wait....")

outfilename = 'output.xlsx'


# prepare directory

# # cleanup directory
# if os.path.exists("xpdf") and os.path.isdir("xpdf"):
#     print("xpdf exists, deleting it....")
#     shutil.rmtree("xpdf")
#f.convert_pdf_to_html('test1.pdf')

# cleanup directory
if os.path.exists("project") and os.path.isdir("project"):
    print("Deleting old project flies...")
    shutil.rmtree("project")

print("creating new project directory")
# create directory for the project
Path(PR.DIR_TABULATED_CSV).mkdir(parents=True, exist_ok=True)


price_list = PdfDoc(infilename, page_start=1, n_pages=1)
