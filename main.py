import sys  # access to functions and variables that allow for working with Python interpreter
from classes import *

# do refactor to make a row a custom object with all the methods

args = sys.argv  # get the list of arguments

infilename = args[1] if len(args) == 2 else 'test1.pdf'  # infilename is the args[1] or default to 'test1.pdf'

print(f"Working on {infilename}\nPlease wait....")

outfilename = 'output.xlsx'

price_list = PdfDoc(infilename, 1, 2)
