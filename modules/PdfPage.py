import csv

import tabula

from modules import PROJ_CONST as PR
from modules.PdfLine import PdfLine
from modules.PageColorTable import PageColorTable
from modules.PageProductTable import PageProductTable


class PdfPage:
    """ converts Pdf page to csv, creates a list of PdfLine objects for each line and passes it to PdfProductTable and PdfColorTable"""

    def __init__(self, infilename, pagenumber):
        self.midfilename = '{}tabulated_{}.csv'.format(PR.DIR_TABULATED_CSV, pagenumber)
        self.list_of_csv_rows = None  # contain list of rows from the csv file obtained from tabula
        # read the one page from pdf file with tabula
        tabula.convert_into(infilename, self.midfilename, output_format='csv', pages=pagenumber, stream=True)

        # read the csv file call it csvfile
        with open(self.midfilename, newline='') as csvfile:
            readerObject = csv.reader(csvfile, dialect='excel')  # returns reader object that is an iterator
            self.list_of_csv_rows = list(readerObject)

        self._pdf_line_list = [PdfLine(line) for line in self.list_of_csv_rows]  # constructs list of PdfLine objects
        self._product_table = PageProductTable(self._pdf_line_list, pagenumber)
        self._color_table = PageColorTable(self._pdf_line_list, pagenumber)