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
        self.html_page_data_set = set()
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

        self.html_page_data_set = html_parser.page_data_set
        self.html_page_data_list = html_parser.page_data_list

        # print(f"Html data set: {html_parser.page_data_set}")  # output the pagedata_set for testing+
        # print(f"Html data list:")
        # for word in html_parser.page_data_list:
        #     print(word)

        self._contains_color_table = self.contains_color_table()

        # constructs list of PdfLine objects
        self._pdf_line_list = [PdfLine(line, self.html_page_data_set, self._contains_color_table) for line in
                               self.list_of_csv_rows]

        self._color_list = None
        if self._contains_color_table:
            if self.tabula_detected_color_table():
                self._color_list = self.extract_color_list_from_tabula()
            else:
                self._color_list = self.extract_color_list_from_html()

        # print(
        #     f"contains color_table: {self._contains_color_table} tabula detected it {self.tabula_detected_color_table()}")
        # print("color_list: ", self._color_list)

        self._product_table = PageProductTable(self._pdf_line_list, pagenumber, self._color_list)

    def extract_color_list_from_tabula(self):
        """if color_table below, extract colors from it"""
        color_list = []
        color_table_header_encountered = False
        for line in self._pdf_line_list:
            if line._is_color_table_header:
                color_table_header_encountered = True
            if line.contains_color() and color_table_header_encountered:
                color_list.append(line.find_item_color())
        return color_list

    def extract_color_list_from_html(self):
        """ color code contains digit can use that too"""
        color_list = []
        color_table_header_encountered = False
        index = 0
        for item in self.html_page_data_list:
            if "COLORS" in item:
                color_table_header_encountered = True
                continue
            if "Customer" in item:
                break
            if color_table_header_encountered:
                if index % 2 == 0:
                    word = ""
                    word += " " + item
                    index += 1
                else:
                    word += " " + item
                    color_list.append(" ".join(word.split()))
                    index += 1
        return color_list

    def contains_color_table(self):
        contains = False
        for token in self.html_page_data_set:
            if "COLORS" in token:
                contains = True
        return contains

    def tabula_detected_color_table(self):
        detected = False
        for line in self._pdf_line_list:
            for item in line._row:
                if "COLORS" in item:
                    detected = True
        return detected
