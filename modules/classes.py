import TEMPLATE


class ExcelTable:
    def __init__(self):
        current_line = 0


class ExcelLine():
    def __init__(self, ):
        current_line = 0

    def fill_data(self):
        pass


class CsvLine:
    line_len = len(TEMPLATE.HEADER)  # line must be of the length of the template header

    def __init__(self):
        self._line = []  # list of values corresponding to the header in order

    def set_value(self, i, value):
        """ sets the value of the list at index i"""
        self._line[i] = value

    def get_line(self):
        return self._line

    def fill_data(self):
        """ takes data from Excel_table_row and puts it in the csv_row according to business logic"""
        pass


class CsvTable:
    """ contains final csv data in the template in the linelist"""
    header = TEMPLATE.HEADER  # list of attributes of the of the csv template

    def __init__(self):
        self._current_line = 0
        self._line_list = []  # list of Csv_line objects
        self.fill_header()

    def fill_header(self):
        self._line_list[self._current_line] = CsvTable.header
        self._current_line += 1

    def append_line(self, line):
        self._line_list.append(line)
        self._current_line += 1

    def get_csv_table(self):
        """ :returns list of lists that represent the table as rows"""
        table = [item.get_line() for item in self._line_list]
        return table

    def fill_data(self, excel_table):
        """fills the csv table for the template"""
        for row in excel_table:
            csv_line = CsvLine()
            csv_line.fill_data()
            self.append_line(csv_line)
