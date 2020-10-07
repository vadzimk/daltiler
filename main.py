import sys

from modules.classes import *
from modules.func import *


cleanup()
create_project()


args = sys.argv  # get the list of arguments



infilename = args[1] if len(args) == 2 else 'test1.pdf'  # infilename is the args[1] or default to 'test1.pdf'

print(f"Working on {infilename}\nPlease wait....")


price_list = PdfDoc(infilename, page_start=1, n_pages=1)

# f.convert_pdf_to_html('test1.pdf')




