from PdfLine import PdfLine

import tabula

import TEMPLATE
import PDF_CONST as PFC
import csv
import pandas


class PdfDoc:
    """ manages a list of PdfPage objects"""

    def __init__(self, in_file_name, page_start=1, n_pages=1):
        """by default grabs the first page only"""
        self._pages = [PdfPage(in_file_name, pagenumber=i) for i in
                       range(page_start, page_start + n_pages)]  # list of PdfPage objects


class PdfPage:
    """ converts Pdf page to csv, creates a list of PdfLine objects for each line and passes it to PdfProductTable and PdfColorTable"""

    def __init__(self, infilename, pagenumber):
        self.midfilename = 'tabulated_{}.csv'.format(pagenumber)
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


class PageProductTable:
    """ contains products in a dictionary """

    def __init__(self, lines, page_number):
        self.__products = {key: [] for key in PFC.PRODUCT_TABLE_FIELDS}  # dictionary that will hold the items of the table
        self._series_name = None
        self._group = None
        self._subgroup = None  # subgroup is like "BULLNOSE"
        self._vendor_code = None
        self._item_size = None
        self._item_color = None
        self._units_per_carton = None
        self._units_of_measure = None
        self._unit_price = None

        self.build_table(lines)  # put products in the dictionary

        # demonstrate product table as data frame for testing
        df = pandas.DataFrame(self.__products)
        df.to_csv('data_frame{}.csv'.format(page_number), index=False)  # export product table as csv

    def build_table(self, lines):
        """ sees what fields are detected by the PdfLine and builds product table"""
        for line in lines:
            """collect the fields"""
            self._series_name = line.find_series_name() if line.find_series_name() else self._series_name
            self._group = line.find_group() if line.find_group() else self._group
            self._subgroup = line.find_subgroup() if line.find_subgroup() else self._subgroup
            self._vendor_code = line.find_vendor_code() if line.find_vendor_code() else self._vendor_code
            self._item_size = line.find_item_size() if line.find_item_size() else self._item_size
            self._item_color = line.find_item_color() if line.find_item_color() else self._item_color
            self._units_per_carton = line.find_units_per_carton() if line.find_units_per_carton() else self._units_per_carton
            self._units_of_measure = line.find_units_of_measure() if line.find_units_of_measure() else self._units_of_measure
            self._unit_price = line.find_unit_price() if line.find_unit_price() else self._unit_price

            if line.is_table_row():
                """push properties to the dictionary"""
                for key in PFC.PRODUCT_TABLE_FIELDS:
                    value = eval("self.%s" % (key))  # line at key
                    self.__products[key].append(value)

    def get_products(self):
        """@:returns the dictionary of products representing product table of the page"""
        return self.__products


class PageColorTable:
    """ retrieves set of colors to map to each product on the page"""

    def __init__(self, lines, page_number):
        self.colors = []

    def get_list_of_colors(self):
        return self.colors


class ExcelTable:
    def __init__(self):
        current_line = 0


class ExcelLine():
    def __init__(self, ):
        current_line = 0

    def fill_data(self):
        pass


class CsvLine:
    line_len = len(TEMPLATE.HEADER)  # line must be of the length of the template header

    def __init__(self):
        self._line = []  # list of values corresponding to the header in order

    def set_value(self, i, value):
        """ sets the value of the list at index i"""
        self._line[i] = value

    def get_line(self):
        return self._line

    def fill_data(self):
        """ takes data from Excel_table_row and puts it in the csv_row according to business logic"""
        pass


class CsvTable:
    """ contains final csv data in the template in the linelist"""
    header = TEMPLATE.HEADER  # list of attributes of the of the csv template

    def __init__(self):
        self._current_line = 0
        self._line_list = []  # list of Csv_line objects
        self.fill_header()

    def fill_header(self):
        self._line_list[self._current_line] = CsvTable.header
        self._current_line += 1

    def append_line(self, line):
        self._line_list.append(line)
        self._current_line += 1

    def get_csv_table(self):
        """ :returns list of lists that represent the table as rows"""
        table = [item.get_line() for item in self._line_list]
        return table

    def fill_data(self, excel_table):
        """fills the csv table for the template"""
        for row in excel_table:
            csv_line = CsvLine()
            csv_line.fill_data()
            self.append_line(csv_line)
