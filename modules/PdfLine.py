import PDF_CONST as PFC


class PdfLine:
    """A line of the Pdf input file"""

    @staticmethod
    def token_is_blank(csv_list_item):
        return csv_list_item == '\"\"' or not csv_list_item

    def __init__(self, tabula_csv_reader_list_line, page_data_set, color_table_below):
        """ @:param page_data_set for better detection of tokens"""
        self._page_data_set = page_data_set
        self._tablula_line = tabula_csv_reader_list_line
        self._row = self.treat_row()

        self._color_table_below = color_table_below

        self._row_len = len(self._row)  # number of items in the list representing the row
        self._num_blanks = self.count_blanks()
        # self._all_cells_filled = self.all_cells_filled()  # applies to a table row only
        self._is_color_table_header = self.is_color_table_header()
        self._is_color_table_row = self.is_color_table_row()
        self._is_product_table_row = self.is_product_table_row()



    def contains_series(self):
        """ detects series name in the row"""
        return PFC.DETECT_SERIES_SET.issubset(set(self._tablula_line))

    def find_series_name(self):
        """ if row contains series then returns it otherwise returns None """
        name = None
        if self.contains_series():
            if "#" in self._tablula_line[0]:
                name = self._tablula_line[0].replace('#', '') + " " + self._tablula_line[1]
            elif "#" in self._tablula_line[1]:
                name = self._tablula_line[0] + " " + self._tablula_line[2]
            name = " ".join(name.split())  # remove multiple spaces
        return name

    def count_blanks(self):
        """ counts number of blanks in a given row"""
        count = 0
        for token in self._tablula_line:
            if PdfLine.token_is_blank(token):
                count += 1
        return count

    def contains_group(self):
        """if length of row is 1 and the 0th item is not empty string
         then it contains group name"""
        contains = False
        if self._num_blanks == self._row_len - 1 and not PdfLine.token_is_blank(
                self._row[0]) and not self._is_color_table_header:
            contains = True
        return contains

    def find_group(self):
        group_name = None
        if self.contains_group():
            group_name = self._row[0]
        return group_name

    def contains_subgroup(self):
        return self._is_product_table_row

    def subgoup_index(self):
        index = 0
        if (not self._row[0] and not self._row[1] and len(self._row) >= 7) or (
                len(self._row) == 6 or len(self._row) == 5):
            # row doesn't have value of size and vendor_code (it's above) the first nonempty item will contain subgroup
            i = 0  # start looking from index
        elif not self._row[1]:
            i = 3  # row contains values of size and vendor code befroe the subgroup and row[1] is empty
        else:
            i = 2  # row contains values of size and vendor code before the subgroup and there are no empty cells before subgroup(treated cell)

        while i < len(self._row):
            if self._row[i]:
                index = i
                break
            i += 1
        return index

    def find_subgroup(self):
        subgroup_name = None
        if self.contains_subgroup():
            index = self.subgoup_index()
            subgroup_name = self._row[index]
        return subgroup_name

    def contains_item_size(self):
        return self._is_product_table_row
        # return self.all_cells_filled()

    def find_item_size(self):
        item_size = None
        if self.contains_item_size():
            ITEM_SIZE_INDEX = 0
            item_size = "".join(self._row[ITEM_SIZE_INDEX].split()[0:3])
        return item_size

    def contains_vendor_code(self):
        # return self.all_cells_filled()
        return self._is_product_table_row

    def vendor_code_index(self):
        index = 0
        if (not self._row[0] and not self._row[1] and len(self._row) >= 7) or (
                len(self._row) == 6 or len(self._row) == 5):
            # row doesn't have value of size and vendor_code (it's above) the first nonempty item will contain subgroup
            return None
        elif not self._row[1]:
            i = 2  # row contains values of size and vendor code befroe the subgroup and row[1] is empty
        else:
            i = 1  # row contains values of size and vendor code before the subgroup and there are no empty cells before subgroup(treated cell)

        while i < len(self._row):
            if self._row[i]:
                index = i
                break
            i += 1
        return index


    def find_vendor_code(self):
        code = None
        if self.contains_vendor_code():
            index = self.vendor_code_index()
            if index == None:
                return code
            if '*' in self._row[index]:
                code = self._row[index].split(' ')[-2]
            else:
                code = self._row[index].split(' ')[-1]  # the last item of the returned by split list
        return code

    def contains_color(self):
        contains = False
        if not self._color_table_below and self._is_product_table_row:
            contains = True
        elif self._color_table_below and self._is_product_table_row:
            contains = False
        elif self._color_table_below and self._is_color_table_row and not self._is_color_table_header:  # this is a color table row and it contains color if _row_len==3
            contains = True
        return contains

    def color_index(self):  # finish this
        index = None
        i = self.subgoup_index()+1 # start from index after subgroup

        while i < len(self._row):
            if self._row[i]:
                index = i
                break
            i += 1
        return index

    def find_item_color(self):
        color = None
        if self.contains_color() and self._is_product_table_row:
            index = self.color_index()
            color = self._row[index]
        elif self.contains_color() and self._is_color_table_row:
            color = ' '.join(self._row).strip()
        return color

    def contains_units_per_carton(self):
        pass

    def find_units_per_carton(self):
        upc = None
        if self._is_product_table_row:
            upc = self._row[-3]
        return upc

    def find_units_of_measure(self):
        uom = None
        if self._is_product_table_row:
            uom = self._row[-2]
        return uom

    def find_unit_price(self):
        up = None
        if self._is_product_table_row:
            up = self._row[-1]
        return up

    def is_product_table_row(self):
        """returns true if the row from midfile to be output in the outfile"""
        row_set = set(self._row)
        is_valid = False
        if not self.contains_series() and not self.contains_group() and not self._is_color_table_row and not self._is_color_table_header and PFC.DETECT_SERIES_SET.isdisjoint(
                row_set) and PFC.EMPTY_LINE_FLAGS.isdisjoint(
            row_set):
            is_valid = True
        return is_valid

    def is_color_table_header(self):
        is_header = False
        for item in self._row:
            if "COLORS" in item:
                is_header = True
        return is_header

    def is_color_table_row(self):
        is_ctr = False
        is_ctr = self._color_table_below and self._row_len <= 3 and self._row_len - self._num_blanks <= 2 and not self._is_color_table_header
        return is_ctr

    def extract_first_match(self, phrase):
        """ @:param phrase is a string with spaces that needs to be broken in several tokens that are present in page_data_set
        @:returns recursively smaller phrase that is either empty string or contained in the page_data_set """
        if len(phrase) == 0:
            return phrase
        elif phrase in self._page_data_set:
            return phrase
        else:
            return self.extract_first_match(" ".join(phrase.split()[:-1]))  # remove the last word from the token

    def treat_row(self):
        """ compares token in row to the html dataset and separates string into items that are present in the html dataset"""
        tabula_line = []
        for token in self._tablula_line:
            tabula_line.append(" ".join(token.split()))

        row = []
        for phrase in tabula_line:
            if phrase == "":
                row.append(phrase)
            else:
                i = 0  # holds index of the next place to search for a token
                while i < len(phrase):
                    le = len(phrase[i:])
                    fixed = self.extract_first_match(phrase[i:])

                    if not fixed == '':
                        row.append(fixed)
                    i = phrase.index(fixed) + len(fixed) + 1  # points to the beginning of next token in phrase
                    if i < le:
                        phrase = phrase[i:]  # make next token first
                    else:
                        break
                    i = 0

        return row
