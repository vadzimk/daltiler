import sys

from modules.classes import *
from modules.func import *
import subprocess

cleanup()
create_project()


args = sys.argv  # get the list of arguments



infilename = args[1] if len(args) == 2 else 'test36.pdf'  # infilename is the args[1] or default to 'test1.pdf'

# ==============================================================
convert_to_html(infilename)
#     =============================================================
infilename_n_pages = determine_n_pages(infilename)

print(f"Working on {infilename}\nPlease wait....")
if infilename_n_pages != 1:
    print(f"Found {infilename_n_pages} pdf pages.")
else:
    print(f"Found {infilename_n_pages} pdf page.")



price_list = PdfDoc(infilename, page_start=1, n_pages=5)

# f.convert_pdf_to_html('test1.pdf')




