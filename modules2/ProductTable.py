import modules2.PDF_CONST as PFC
import pprint

class ProductTable:
    def __init__(self, page_number, dt, guessed_rows, colors):
        self.__dt = dt
        self.__colors = colors
        self.__products = {key: [] for key in
                           PFC.PRODUCT_TABLE_FIELDS}  # dictionary that will hold the items of the table
        self.guessed_rows_strings = [self.join_list_items(item) for item in
                                     guessed_rows]  # joins guessed rows and retrurns a list of strings
        #  fields of the csv data frame:
        self._pagenumber = page_number

        self._series_name = None
        self._group = None
        self._subgroup = None  # subgroup is like "BULLNOSE"
        self._vendor_code = None
        self._item_size = None
        self._item_color = None
        self._units_per_carton = None
        self._units_of_measure = None
        self._unit_price = None

        print(f"product table init page{self._pagenumber}")

        # TODO continue this file

    def build_table(self):
        """ sees what fields are detected by the PdfLine and builds product table"""
        for line in self.__dt.lines:  # line comes form fixed column recognition

            """TODO skip lines that are not valid, check if line is guessed list if so than it is valid, """
            cur_line_string = self.join_list_items(line._tabula_line)
            valid_line = False
            # for item in self.guessed_rows_strings:
            #     if item in cur_line_string:
            #         valid_line = True
            if cur_line_string in self.guessed_rows_strings or (
                    'Units' in cur_line_string and 'Price' in cur_line_string):
                valid_line = True

            if valid_line:  # line matches the auto guessed row
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
                if self.__colors:  # if color list is present, a product row will be appended the number of colors times
                    multiplier = len(self.__colors)

                if line._is_product_table_row and self._series_name:
                    # print("is_product_table_row: ", line._is_product_table_row)
                    # print("_series_name", self._series_name)

                    """push properties to the dictionary"""
                    for i in range(multiplier):
                        for key in PFC.PRODUCT_TABLE_FIELDS:
                            if self.__colors and key == "_item_color":
                                value = self.__colors[i]
                            else:
                                value = eval("self.%s" % (key))  # line at key
                            self.__products[key].append(value)

            # print(valid_line, cur_line_string)
        # print('product table')
        # pprint.pp(self.__products)

    @staticmethod
    def join_list_items(list_obj):
        line_string_list = [str(item) for item in list_obj]  # strignify any non-string types of items of the list
        line_string = "".join(line_string_list)  # join all items in one string (with no spaces between items)
        line_string = "".join(line_string.split())
        return line_string

    @property
    def products(self):
        return self.__products