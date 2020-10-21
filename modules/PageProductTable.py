import pandas

import modules.PDF_CONST as PFC
from modules import PROJ_CONST as PR
import csv


class PageProductTable:
    """ contains products in a dictionary """

    def __init__(self, lines, guessed_rows, page_number, colors):
        self._pagenumber = page_number
        self.lines = lines
        # print("guessed_rows")
        # for row in guessed_rows:
        #     print(row)
        self.guessed_rows_strings = [self.join_list_items(item) for item in guessed_rows]  # joins guessed rows and retrurns a list of strings
        # print("guessed_strings:")
        # for string in self.guessed_rows_strings:
        #     print(string)
        # # print("---tabulalines:")
        # # for line in lines:
        # #     print(line._tabula_line)
        # print("__ end")
        self.colors = colors

        self.__products = {key: [] for key in
                           PFC.PRODUCT_TABLE_FIELDS}  # dictionary that will hold the items of the table
        #  fields of the csv data frame:
        self._series_name = None
        self._group = None
        self._subgroup = None  # subgroup is like "BULLNOSE"
        self._vendor_code = None
        self._item_size = None
        self._item_color = None
        self._units_per_carton = None
        self._units_of_measure = None
        self._unit_price = None

        self.build_table()  # put products in the dictionary

        # TODO keep this
        # export product table as csv
        # df = pandas.DataFrame(self.__products)
        # df.to_csv('{}data_frame{}.csv'.format(PR.DIR_PRODUCT_TABLES, page_number), index=False)

        # # export treated rows as csv
        # self.export_treated_rows()

    def build_table(self):
        """ sees what fields are detected by the PdfLine and builds product table"""
        for line in self.lines:  # line comes form fixed column recognition

            """TODO skip lines that are not valid, check if line is guessed list if so than it is valid, """
            cur_line_string = self.join_list_items(line._tabula_line)
            valid_line = False
            # for item in self.guessed_rows_strings:
            #     if item in cur_line_string:
            #         valid_line = True
            if cur_line_string in self.guessed_rows_strings or ('Units' in  cur_line_string and 'Price' in cur_line_string):
                valid_line = True

            if valid_line: # line matches the auto guessed row
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

                multiplier = 1  # number of times the row must be multiplied
                if self.colors:  # if color list is present, a product row will be appended the number of colors times
                    multiplier = len(self.colors)

                if line._is_product_table_row and self._series_name:
                    # print("is_product_table_row: ", line._is_product_table_row)
                    # print("_series_name", self._series_name)

                    """push properties to the dictionary"""
                    for i in range(multiplier):
                        for key in PFC.PRODUCT_TABLE_FIELDS:
                            if self.colors and key == "_item_color":
                                value = self.colors[i]
                            else:
                                value = eval("self.%s" % (key))  # line at key
                            self.__products[key].append(value)

            # print(valid_line, cur_line_string)

    def get_products(self):
        """@:returns the dictionary of products representing product table of the page"""
        return self.__products

    # def export_treated_rows(self):
    #     """ export treated rows as csv"""
    #     frame = []
    #     for line in self.lines:
    #         frame.append(line._row)
    #     with open("{}treated{}.csv".format(PR.DIR_TREATED_ROWS, self._pagenumber), "w", newline='') as f:
    #         wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    #         wr.writerows(frame)

    def join_list_items(self, list_obj):
        line_string_list = [str(item) for item in list_obj]  # strignify any non-string types of items of the list
        line_string = "".join(line_string_list)  # join all items in one string (with no spaces between items)
        line_string = "".join(line_string.split())
        return line_string
