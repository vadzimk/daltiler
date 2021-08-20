from modules2.PdfLine import PdfLine


class DataTable:
    def __init__(self, rows):
        self.__csv_rows = rows
        self.__pdf_lines = [PdfLine(line) for line in self.__csv_rows]
        self.__title = self.extract_title_key(self.__csv_rows)

    @staticmethod
    def extract_title_key(rows):
        try:
            header = "".join(rows[0][0:-3]).replace('#', '').replace(" ", "")

            # print(header)
            return header
        except TypeError:
            return ''

    @property
    def title(self):
        return self.__title
    @property
    def lines(self):
        return self.__pdf_lines
