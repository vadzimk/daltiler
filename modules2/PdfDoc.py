import json
import multiprocessing
import queue
import threading

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
        self.__callback = lambda p: None
        self.pdf_page_queue = queue.Queue()

    def pdf_pages_manager(self):
        """ exclusively creates pages on PdfDoc obj i.e.
        appends to __pages"""
        print("pages_manager started")
        counter = 0
        while True:
            page = self.pdf_page_queue.get()
            self.__pages.append(page)
            counter += 1
            print(f"counter {counter}")
            self.__callback(counter)
            self.pdf_page_queue.task_done()

    def create_pages_in_threads(self, callback):
        self.__callback = callback
        pages_manager_t = threading.Thread(target=self.pdf_pages_manager, daemon=True)
        pages_manager_t.start()
        del pages_manager_t

        THREAD_N = max(multiprocessing.cpu_count()-1, 1)
        workers = []
        next_batch_page_n = self.__page_start

        while next_batch_page_n < self.__page_start + self.__n_pages:
            for i in range(min(THREAD_N, self.__page_start + self.__n_pages - next_batch_page_n)):
                page_num = next_batch_page_n + i
                coordinates = self.extract_page_data_from_json_data(self.__jsondata, page_num)

                t = threading.Thread(target=self.__worker, args=(page_num, coordinates))
                workers.append(t)
                t.start()

            for t in workers:
                t.join()
            next_batch_page_n += THREAD_N
        self.pdf_page_queue.join()

    def __worker(self, page_num, coordinates):
        worker_page = PdfPage(
            infilename=self.__in_file_name,
            pagenumber=page_num,
            coordinates=coordinates
        )
        self.pdf_page_queue.put(worker_page)

    def create_pages(self, callback=lambda p: None):
        """ create pages in one thread """
        self.__pages = [PdfPage(
            infilename=self.__in_file_name,
            pagenumber=i,
            coordinates=self.extract_page_data_from_json_data(json_data=self.__jsondata, pagenumber=i),
            callback = callback
        ) for i in range(self.__page_start, self.__page_start + self.__n_pages)]

    def create_product_tables(self):
        self.__pages.sort(key=lambda i: i.pagenumber)
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

        # patch cumulative dictionary where
        # _group ends with  "CONT'D" replace to "" remove any " - "
        # if empty _item_size	_vendor_code, copy from the previous index

    def patch_cumulative_dictionary(self):
        index = None
        for i, group in enumerate(self.__all_pages_product_dict['_group']):
            if "CONT'D" in group:
                item_sizes = self.__all_pages_product_dict['_item_size']
                vendor_codes = self.__all_pages_product_dict['_vendor_code']
                if not item_sizes[i]:
                    item_sizes[i] = item_sizes[i - 1]
                if not vendor_codes[i]:
                    vendor_codes[i] = vendor_codes[i - 1]
                self.__all_pages_product_dict['_group'][i] = group.replace("CONT'D", "").rstrip(' -')

        # print(f"cumulative dict: {self.__list_of_all_product_dicts}")

    def export_cumulative_dict(self, path=PR.DOC_PRODUCT_TABLE):
        df = pandas.DataFrame(self.__all_pages_product_dict)
        df.to_csv(path, index=False)
        return True

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
