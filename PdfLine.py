import PCONST as PC


class PdfLine:
    """A line of the Pdf input file"""

    @staticmethod
    def token_is_blank(csv_list_item):
        return csv_list_item == '\"\"' or not csv_list_item

    def __init__(self, tabula_csv_reader_list_line):
        self._row = tabula_csv_reader_list_line  # list corresponding to a line in the csv_reader file
        self._row_len = len(self._row)  # number of items in the list representing the row
        self._num_blanks = self.count_blanks()
        self._is_table_row = False
        self._all_cells_filled = self.all_cells_filled()  # applies to a table row only

        self._series_name = self.find_series_name()
        self._group = self.find_group()
        self._subgroup = self.find_subgroup()  # subgroup is like "BULLNOSE"
        self._vendor_code = self.find_vendor_code()
        self._item_size = self.find_item_size()
        self._item_color = self.find_item_color()
        self._units_per_carton = self.find_units_per_carton()
        self._units_of_measure = self.find_units_of_measure()
        self._unit_price = self.find_unit_price()

    def contains_series(self):
        """ detects series name in the row"""
        return PC.DETECT_SERIES_SET.issubset(set(self._row))

    def find_series_name(self):
        """ if row contains series then returns it otherwise returns None """
        name = None
        if self.contains_series():
            if "#" in self._row[0]:
                name = self._row[0].replace('#', '') + " " + self._row[1]
            elif "#" in self._row[1]:
                name = self._row[0] + " " + self._row[2]
            name = " ".join(name.split())  # remove multiple spaces
        return name

    def count_blanks(self):
        """ counts number of blanks in a given row"""
        count = 0
        for token in self._row:
            if PdfLine.token_is_blank(token):
                count += 1
        return count

    def contains_group(self):
        """if length of row is 1 and the 0th item is not empty string
         then it contains group name"""
        contains = False
        if self._num_blanks == self._row_len - 1 and not PdfLine.token_is_blank:
            contains = True
        return contains

    def find_group(self):
        group_name = None
        if self.contains_group():
            group_name = self._row[0]
        return group_name

    def contains_subgroup(self):
        contains = False
        # if row has 7 columns and at least 5 of them are not blank (for now)
        if self._row_len == max(PC.ITEM_ROW_LEN) and self._row_len - self._num_blanks in PC.ITEM_ROW_LEN:
            contains = True
        return contains

    def find_subgroup(self):
        subgroup_name = None
        if self.contains_subgroup():
            SUBGROUP_INDEX = 2
            subgroup_name = self._row[SUBGROUP_INDEX]
        return subgroup_name

    def all_cells_filled(self):
        all_filled = False
        # if row has 7 columns and at least 6 of them are not blank (for now)
        if self._row_len == max(PC.ITEM_ROW_LEN) and self._row_len - self._num_blanks == 6:
            all_filled = True
        return all_filled

    def contains_vendor_code(self):
        return self.all_cells_filled()

    def find_vendor_code(self):
        code = None
        if self.contains_vendor_code():
            if '*' in self._row[PC.VENDOR_CODE_INDEX]:
                code = self._row[PC.VENDOR_CODE_INDEX].split()[-2]
            else:
                code = self._row[PC.VENDOR_CODE_INDEX].split()[-1]  # the last item of the returned by split list
        return code

    def contains_item_size(self):
        return self.all_cells_filled

    def find_item_size(self):
        item_size = None
        if self.contains_item_size():
            ITEM_SIZE_INDEX = 0
            item_size = "".join(self._row[ITEM_SIZE_INDEX].split()[0:3])
        return item_size

    def contains_color(self):
        return True

    def find_item_color(self):
        color = None
        if self.contains_color():
            color = self._row[3]
        return color

    def find_units_per_carton(self):
        upc = self._row[4]
        return upc

    def find_units_of_measure(self):
        uom = self._row[5]
        return uom

    def find_unit_price(self):
        up = self._row[6]
        return up

    def is_table_row(self):
        """returns true if the row from midfile to be output in the outfile"""
        row_set = set(self._row)
        is_valid = False
        if self._row_len - self._num_blanks in PC.ITEM_ROW_LEN and PC.DETECT_SERIES_SET.isdisjoint(
                row_set) and PC.EMPTY_LINE_FLAGS.isdisjoint(
            row_set):
            is_valid = True
        return is_valid
