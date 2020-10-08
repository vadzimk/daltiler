import pandas

import PDF_CONST as PFC
from modules import PROJ_CONST as PR


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

        # export product table as csv
        df = pandas.DataFrame(self.__products)
        df.to_csv('{}data_frame{}.csv'.format(PR.DIR_PRODUCT_TABLES, page_number), index=False)

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

            if line.is_product_table_row():
                """push properties to the dictionary"""
                for key in PFC.PRODUCT_TABLE_FIELDS:
                    value = eval("self.%s" % (key))  # line at key
                    self.__products[key].append(value)

    def get_products(self):
        """@:returns the dictionary of products representing product table of the page"""
        return self.__products