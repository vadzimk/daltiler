import modules.PDF_CONST as PFC


class PdfLine:
    """A line of the Pdf input file"""

    @staticmethod
    def token_is_blank(csv_list_item):
        return csv_list_item == '\"\"' or not csv_list_item

    def __init__(self, tabula_csv_reader_list_line):
        """ @:param page_data_set for better detection of tokens"""
        # self._page_data_set = page_data_set
        self._tabula_line = tabula_csv_reader_list_line
        # self._row = self.treat_row()  # check for matches with page_data_set

        # self._row_len = len(self._row)  # number of items in the list representing the row
        self._num_blanks = self.count_blanks()
        # self._all_cells_filled = self.all_cells_filled()  # applies to a table row only
        self._is_color_table_header = self.is_color_table_header()
        self._is_color_table_row = self.is_color_table_row()
        self._is_product_table_row = self.is_product_table_row()

        # print(len(self._row), self._row)

    def contains_series(self):
        """ detects series name in the row"""
        return PFC.DETECT_SERIES_SET.issubset(set(self._tabula_line))

    def find_series_name(self):
        """ if row contains series then returns it otherwise returns None """
        name = None
        cells = []
        # remove Unnamed cells
        if self.contains_series():
            for item in self._tabula_line[:-3]:
                if "Unnamed" not in item:
                    cells.append(item)

            name = "".join(cells).replace('#', '')
            name = " ".join(name.split()) # remove multiple spaces

        return name

    def count_blanks(self):
        """ counts number of blanks in a given row"""
        count = 0
        for token in self._tabula_line:
            if PdfLine.token_is_blank(token):
                count += 1
        return count

    def contains_group(self):
        """ :returns true if row contains group name, false otherwise"""
        contains = False
        if not self._tabula_line[-1] and not self._tabula_line[-2] and not self._tabula_line[-3]:
            contains = True
        # print("contains group: ", self._tablula_line[-3:], contains, self._tablula_line)
        return contains

    def find_group(self):
        group_name = None
        cells = self._tabula_line[:-3]
        if self.contains_group():
            group_name = "".join(cells)
        return group_name

    def contains_subgroup(self):
        return self._is_product_table_row

    # def subgoup_index(self):
    #     return 2

    def find_subgroup(self):
        subgroup_name = None
        if self.contains_subgroup():
            index = 2
            subgroup_name = self._tabula_line[index]
        return subgroup_name

    def contains_item_size(self):
        return self._is_product_table_row
        # return self.all_cells_filled()

    def find_item_size(self):
        item_size = None
        if self.contains_item_size():
            index = 0
            item_size = self._tabula_line[index]
        return item_size

    def contains_vendor_code(self):
        return self._is_product_table_row

    # def vendor_code_index(self):
    #     return 1

    def find_vendor_code(self):
        code = None
        if self.contains_vendor_code():
            index = 1
            code = str(self._tabula_line[index])
            if '*' in code:
                code = code.split(' ')[0]
        return code

    def contains_color(self):
        contains = False
        if self._is_product_table_row:
            if self._tabula_line[3]:
                contains = True
        return contains

    # def color_index(self):
    #     return 3

    def find_item_color(self):
        # TODO finish if is color table row
        # print("contains_color:", self.contains_color(), "is_header: ", self._is_color_table_header, "is_color_row: ", self._is_color_table_row, self._tablula_line)
        color = None
        if self.contains_color() and self._is_product_table_row:
            index = 3
            color = self._tabula_line[index]
            color = " ".join(color.split())
        # elif self.contains_color() and self._is_color_table_row:
        #     color = ' '.join(self._row).strip()
        return color

    # def contains_units_per_carton(self):
    #     pass

    def find_units_per_carton(self):
        upc = None
        if self._is_product_table_row:
            upc = self._tabula_line[-3]
        return upc

    def find_units_of_measure(self):
        uom = None
        if self._is_product_table_row:
            uom = self._tabula_line[-2]
        return uom

    def find_unit_price(self):
        up = None
        if self._is_product_table_row:
            up = self._tabula_line[-1]
        return up

    def is_product_table_row(self):
        """returns true if the row from midfile to be output in the outfile"""
        row_set = set(self._tabula_line)
        is_valid = False
        if len(self._tabula_line)>6 and not self.contains_series() and not self.contains_group() and not self._is_color_table_row and not self._is_color_table_header and PFC.DETECT_SERIES_SET.isdisjoint(
                row_set) and PFC.EMPTY_LINE_FLAGS.isdisjoint(
            row_set):
            is_valid = True
        return is_valid

    def is_color_table_header(self):
        is_header = False
        for item in self._tabula_line:
            if "COLORS" in str(item):
                is_header = True
        return is_header

    def is_color_table_row(self):
        return False

    # def extract_first_match(self, phrase):
    #     """ @:param phrase is a string with spaces that needs to be broken in several tokens that are present in page_data_set
    #     @:returns recursively smaller phrase that is either empty string or contained in the page_data_set """
    #     if len(phrase) == 0:
    #         return phrase
    #     elif phrase in self._page_data_set:
    #         return phrase
    #     else:
    #         return self.extract_first_match(" ".join(phrase.split()[:-1]))  # remove the last word from the token
    #
    # def treat_row(self):
    #     """ compares token in row to the html dataset and separates string into items that are present in the html dataset"""
    #     tabula_line = []
    #     for token in self._tablula_line:
    #         tabula_line.append(" ".join(str(token).split()))
    #
    #     row = []
    #     for phrase in tabula_line:
    #         if phrase == "":
    #             row.append(phrase)
    #         else:
    #             i = 0  # holds index of the next place to search for a token
    #             while i < len(phrase):
    #                 le = len(phrase[i:])
    #                 fixed = self.extract_first_match(phrase[i:])
    #
    #                 if not fixed == '':
    #                     row.append(fixed)
    #                 i = phrase.index(fixed) + len(fixed) + 1  # points to the beginning of next token in phrase
    #                 if i < le:
    #                     phrase = phrase[i:]  # make next token first
    #                 else:
    #                     break
    #                 i = 0
    #
    #     return row
