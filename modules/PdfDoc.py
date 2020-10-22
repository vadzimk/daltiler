import pandas

from modules import PROJ_CONST as PR, PDF_CONST as PFC
from modules.PdfPage import PdfPage


class PdfDoc:
    """ manages a list of PdfPage objects"""

    def __init__(self, in_file_name, page_start=1, n_pages=1):
        """by default grabs the first page only"""

        self.page_start = page_start
        self.n_pages = n_pages
        self.in_file_name = in_file_name
        self._pages = None
        self.__all_pages_product_dict = {}  # dictionary that will hold the items of all product tables

    def export_cumulative_dict(self):
        df = pandas.DataFrame(self.__all_pages_product_dict)
        df.to_csv(PR.DOC_PRODUCT_TABLE, index=False)

    def create_pages(self):
        _pages = [PdfPage(self.in_file_name, pagenumber=i) for i in
                  range(self.page_start, self.page_start + self.n_pages)]  # list of PdfPage objects
        self._pages = _pages

    def create_product_tables(self):
        for i in range(len(self._pages) - 1):
            self._pages[i].create_product_table(self._pages[i + 1]._color_list)
        self._pages[len(self._pages) - 1].create_product_table()  # ceate last product table with no external color list

    def construct_cumulative_dict(self):
        self.__list_of_all_product_dicts = [page._product_table.get_products() for page in self._pages]

        # construct cumulative dictionary
        for key in PFC.PRODUCT_TABLE_FIELDS:
            self.__all_pages_product_dict[key] = []
            for item in self.__list_of_all_product_dicts:
                self.__all_pages_product_dict[key] += item[key]

        # print(f"cumulative dict: {self.__list_of_all_product_dicts}")

    # # =================== Not used  =======================
    # def create_decending_stack_of_pages(self):
    #     """ :returns a stack onf PdfPage objects with greatest page number first"""
    #     range_start = self.page_start
    #     range_end = self.page_start + self.n_pages
    #
    #     _stack = []
    #
    #     index = range_end - 1
    #     while index >= range_start:
    #         page = PdfPage(self.in_file_name, pagenumber=index)
    #         _stack.append(page)
    #         index -= 1
    #     return _stack
    #
    # def construct_product_tables (self, the_stack):
    #     range_start = self.page_start
    #     range_end = self.page_start + self.n_pages
    #
    #     index = range_end - 1
    #
    #     for i in range(len(the_stack)):
    #         if the_stack[i]._contains_color_table:
    #             the_stack[i].create_product_table()
    #         # else:
