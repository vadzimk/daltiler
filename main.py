import sys

from modules.classes import *
from modules.func import *
import subprocess

cleanup()
create_project()


args = sys.argv  # get the list of arguments



infilename = args[1] if len(args) == 2 else 'test36.pdf'  # infilename is the args[1] or default to 'test1.pdf'

# ==============================================================
# run pdftohtml https://www.xpdfreader.com/pdftohtml-man.html

command ="pdftohtml -q {} {}".format(infilename, PR.DIR_XPDF).split()
pdftohtml_process = subprocess.run(command)


# signal error from pdftohtml process
if pdftohtml_process.returncode:
    print(f"pdftohtml return code: {pdftohtml_process.returncode}")
#     =============================================================


print(f"Working on {infilename}\nPlease wait....")


price_list = PdfDoc(infilename, page_start=1, n_pages=5)

# f.convert_pdf_to_html('test1.pdf')




