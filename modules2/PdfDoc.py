import json

import pandas

from modules2.PdfPage import PdfPage
from modules2 import PDF_CONST as PFC
from modules2 import PROJ_CONST as PR


class PdfDoc:
    def __init__(self, in_file_name, template_json, page_start=1, n_pages=1):
        self.__in_file_name = in_file_name
        self.__page_start = page_start
        self.__n_pages = n_pages
        self.__jsondata = self.read_json_data(template_json)
        self.__pages = []
        self.__list_of_all_product_dicts = []
        self.__all_pages_product_dict = {}  # dictionary that will hold the items of all product tables

    def create_pages(self):
        self.__pages = [PdfPage(
            self.__in_file_name,
            i,
            coordinates=self.extract_page_data_from_json_data(json_data=self.__jsondata, pagenumber=i)
        ) for i in range(self.__page_start, self.__page_start + self.__n_pages)]

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

        #patch cumulative dictionary where
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

    @staticmethod
    def extract_page_data_from_json_data(json_data, pagenumber):
        """ :param json_data is a list of dictionaries containing selections from the whole pdf document
        :param pagenumber is current page number
        :returns page_data - a list of dictionaries containing keys: page, extraction_method, x1, x2, y1, y2, width, height
             which is relevant to the pagenumber only"""
        page_data = [data for data in json_data if data["page"] == pagenumber]
        return page_data


    @staticmethod
    def read_json_data(json_file_name):
        """ :returns list of dictionaries correspoinding to json objects """
        with open(json_file_name, 'r') as json_file:
            data = json.load(json_file)

        return data