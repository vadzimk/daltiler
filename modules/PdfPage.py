import csv

import tabula

from modules.PageProductTable import PageProductTable
from modules import PROJ_CONST as PR
from modules.PdfLine import PdfLine

from modules.func import MyHtmlParser


class PdfPage:
    """ converts Pdf page to csv, creates a list of PdfLine objects for each line and passes it to PdfProductTable and PdfColorTable"""

    def __init__(self, infilename, pagenumber):
        print("page:", pagenumber)
        self.midfilename = '{}tabulated_{}.csv'.format(PR.DIR_TABULATED_CSV, pagenumber)
        self.list_of_csv_rows = None  # contain list of rows from the csv file obtained from tabula
        self._page_data_set = set()
        # read the one page from pdf file with tabula
        tabula.convert_into(infilename, self.midfilename, output_format='csv', pages=pagenumber, stream=True)

        # read the csv file call it csvfile
        with open(self.midfilename, newline='') as csvfile:
            readerObject = csv.reader(csvfile, dialect='excel')  # returns reader object that is an iterator
            self.list_of_csv_rows = list(readerObject)

        #  get data from html pages
        html_parser = MyHtmlParser()

        with open('{}page{}.html'.format(PR.DIR_XPDF, pagenumber), 'r') as file:
            data = file.read().replace('\n', '')
            html_parser.feed(data)

        self._page_data_set = html_parser.page_data_set
        print(f"Html data set: {html_parser.page_data_set}")  # output the pagedata_set for testing

        self._contains_color_table = self.contains_color_table()

        # constructs list of PdfLine objects
        self._pdf_line_list = [PdfLine(line, self._page_data_set, self._contains_color_table) for line in
                               self.list_of_csv_rows]

        # if color_table below, extract colors from it
        self._color_list = None
        if self._contains_color_table:
            self._color_list = [line.find_item_color() for line in self._pdf_line_list if
                                line.contains_color()]  # list comprehension with if condition at the end(if-else goes at the front)

        self._product_table = PageProductTable(self._pdf_line_list, pagenumber, self._color_list)

    def contains_color_table(self):
        contains = False
        for token in self._page_data_set:
            if "COLORS" in token:
                contains = True
        return contains
