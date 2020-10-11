import pandas

import PDF_CONST as PFC
from modules import PROJ_CONST as PR
from modules.PdfPage import PdfPage


class PdfDoc:
    """ manages a list of PdfPage objects"""

    def __init__(self, in_file_name, page_start=1, n_pages=1):
        """by default grabs the first page only"""
        self._pages = [PdfPage(in_file_name, pagenumber=i) for i in
                       range(page_start, page_start + n_pages)]  # list of PdfPage objects

        self.__list_of_all_product_dicts = [page._product_table.get_products() for page in self._pages]

        self.__all_pages_product_dict = {}  # dictionary that will hold the items of all product tables

        # construct cumulative dictionary
        for key in PFC.PRODUCT_TABLE_FIELDS:
            self.__all_pages_product_dict[key] = []
            for item in self.__list_of_all_product_dicts:
                self.__all_pages_product_dict[key] += item[key]

        # print(f"cumulative dict: {self.__list_of_all_product_dicts}")

    def export_cumulative_dict(self):
        df = pandas.DataFrame(self.__all_pages_product_dict)
        df.to_csv('{}product_table.csv'.format(PR.DIR_PROJECT), index=False)