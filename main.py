import sys

from modules.classes import *
from modules.func import *
import subprocess

cleanup()
create_project()

args = sys.argv  # get the list of arguments

infilename = ask_for_filename(args) or 'test36.pdf'
print(f"Chosen file: {infilename}")
infilename_n_pages = determine_n_pages(infilename)
n_pages_to_process = ask_for_n_pages(infilename_n_pages) or 1
print(f"Chosen number of pages to process: {n_pages_to_process}.")

convert_to_html(infilename)

print(f"Working on {infilename}\nPlease wait....")

price_list = PdfDoc(infilename, page_start=1, n_pages=n_pages_to_process)

# f.convert_pdf_to_html('test1.pdf')
