import pprint

from modules2.PdfLine import PdfLine


class DataTable:
    def __init__(self, rows, template_rows):
        self.__csv_rows = rows
        self.__template_rows = template_rows

        # TODO PdfLine got a new argument use it to extract names that get fused
        self.__pdf_lines = [PdfLine(f_row, t_row) for f_row, t_row in self.extract_pdf_lines(self.__csv_rows, self.__template_rows)]
        self.__title = self.extract_title_key(self.__csv_rows)

    @staticmethod
    def extract_pdf_lines(fixed_rows, template_rows):
        """ @return a list of tuples that a pdf line would take
        tuple (fixed_line, template_line)
        """
        result =[]
        # print('\n')
        # print("fixed rows len:",len(fixed_rows))
        # for r in fixed_rows:
        #     print(r)
        # print('-'*20)
        # print("template rows len:",len(template_rows))
        # for r in template_rows:
        #     print(r)
        #
        # print('='*20)
        #
        # print("creating PdfLines")
        for index, f_row in enumerate(fixed_rows):
            # print("index", index)
            # print("t_row: ", t_row)
            # print("f_row", fixed_rows[index])
            try:
                t_row = template_rows[index]
            except IndexError:
                t_row = ['']*len(template_rows[0])

            result.append((f_row, t_row))
        return result


    @staticmethod
    def extract_title_key(rows):
        try:
            header = "".join(rows[0][0:-3]).replace('# ', '').replace(' #', '').replace('§', '').replace(" ", "").rstrip('#')

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

    def __str__(self):
        return pprint.pformat(self.__csv_rows)
