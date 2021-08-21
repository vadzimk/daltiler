import pandas

from modules2.PdfPage import PdfPage
from modules2 import PDF_CONST as PFC
from modules2 import PROJ_CONST as PR


class PdfDoc:
    def __init__(self, in_file_name, page_start=1, n_pages=1):
        self.__in_file_name = in_file_name
        self.__page_start = page_start
        self.__n_pages = n_pages
        self.__pages = []
        self.__list_of_all_product_dicts = []
        self.__all_pages_product_dict = {}  # dictionary that will hold the items of all product tables

    def create_pages(self):
        self.__pages = [PdfPage(self.__in_file_name, i) for i in
                        range(self.__page_start, self.__page_start + self.__n_pages)]

    def create_product_tables(self):
        color_dicts = []
        for page in reversed(self.__pages):
            color_dicts.append(page.color_dict)
            page.make_product_tables(color_dicts)
            page.build_tables()

    def construct_cumulative_dict(self):
        for page in self.__pages:
            for pt in page.product_tables:
                self.__list_of_all_product_dicts.append(pt.products)

        # construct cumulative dictionary
        for key in PFC.PRODUCT_TABLE_FIELDS:
            self.__all_pages_product_dict[key] = []
            for item in self.__list_of_all_product_dicts:
                self.__all_pages_product_dict[key] += item[key]

    #TODO patch cumulative dictionary where
        #
        # _group ends with  "CONT'D" replace to "" remove any " - "
        # if empty _item_size	_vendor_code, copy from the previous index
    def patch_cumulative_dictionary(self):
        index = None
        for i, group in enumerate(self.__all_pages_product_dict['_group']):
            if "CONT'D" in group:
                item_sizes = self.__all_pages_product_dict['_item_size']
                vendor_codes = self.__all_pages_product_dict['_vendor_code']
                if not item_sizes[i]:
                    item_sizes[i] = item_sizes[i-1]
                if not vendor_codes[i]:
                    vendor_codes[i]=vendor_codes[i-1]
                self.__all_pages_product_dict['_group'][i] = group.replace("CONT'D", "").rstrip(' -')

        # print(f"cumulative dict: {self.__list_of_all_product_dicts}")

    def export_cumulative_dict(self):
        df = pandas.DataFrame(self.__all_pages_product_dict)
        df.to_csv(PR.DOC_PRODUCT_TABLE, index=False)
