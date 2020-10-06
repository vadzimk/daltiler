from PdfLine import PdfLine

import tabula

import TEMPLATE
import PCONST as PC
import csv


class PdfDoc:
    """ manages a list of PdfPage objects"""

    def __init__(self, in_file_name, page_start=1, n_pages=1):
        """by default grabs the first page only"""
        self._pages = [PdfPage(in_file_name, pagenumber=i) for i in
                       range(page_start, page_start + n_pages)]  # list of PdfPage objects


class PdfPage:
    """ processes the csv page and feeds all its lines to PdfProductTable and PdfColorTable"""

    def __init__(self, infilename, pagenumber):
        self.midfilename = 'out.csv'
        self.list_of_csv_rows = None  # contain list of rows from the csv file obtained from tabula
        # read the one page from pdf file with tabula
        tabula.convert_into(infilename, self.midfilename, output_format='csv', pages=pagenumber, stream=True)

        # read the csv file call it csvfile
        with open(self.midfilename, newline='') as csvfile:
            readerObject = csv.reader(csvfile, dialect='excel')  # returns reader object that is an iterator
            self.list_of_csv_rows = list(readerObject)

        self._pdf_line_list = [PdfLine(line) for line in self.list_of_csv_rows]  # list of PdfLine objects
        self._product_table = PageProductTable(self._pdf_line_list)
        self._color_table = PageColorTable(self._pdf_line_list)


class PageProductTable:
    """ retrieves only items"""

    def __init__(self, lines):
        self.products = {key: [] for key in PC.PRODUCT_TABLE_FIELDS}  # dictionary that will hold the items of the table
        # for i in range(len(lines)):
        #     print(lines[i]._series_name)

        for line in lines:
            for key in PC.PRODUCT_TABLE_FIELDS:
                value = eval("line.%s" % (key))
                self.products['_series_name'].append(value)
        # ----------------   CONTINUE: PUT LINES IN THE DICTIONARY -----------------------
        # MAYBE MOVE PROPERTIES FROM PDFLINE CLASS INTO THIS CLASS ....?
        print(self.products)

    def get_list_of_products(self):
        return self.products


class PageColorTable:
    """ retrieves set of colors to map to each product on the page"""

    def __init__(self, lines):
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
