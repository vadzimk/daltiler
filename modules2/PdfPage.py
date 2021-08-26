import traceback

import tabula
from tabulate import tabulate
from modules2 import PDF_CONST as PFC
from modules2.DataTable import DataTable
from modules2.ProductTable import ProductTable
import pprint


class PdfPage:
    """ when page is created it reads the pdf doc at that page in necessary modes """

    def __init__(self, infilename, pagenumber, coordinates):
        self.__infilename = infilename
        self.__pagenumber = pagenumber
        self.__coordinates = coordinates
        print("page: ", self.__pagenumber)
        # datatable is a list of rows

        self.__csv_rows = self.read_fixed_columns_tabula()
        self.__guessed_lattice_dfs = self.read_guess_lattice_table_tabula()
        self.__template_rows = self.read_with_json_tabula(self.__infilename, self.__pagenumber, self.__coordinates)

        self.__data_tables = [DataTable(fixed_rows, template_rows) for (fixed_rows, template_rows) in
                              self.make_data_table_rows(self.__csv_rows,
                                                        self.__template_rows)]  # contains list of tables with csv rows that the v1 can recognize

        self.__color_dfs = self.filter_color_dfs(self.__guessed_lattice_dfs)
        # self.print_df_list(self.__color_dfs)
        self.__color_dict = self.make_color_dict()
        # print(self.__color_dict)
        self.__product_tables = []

    def make_product_tables(self, color_dict_list):
        """ for each DataTable create product table using color dict
        @:return list of product tables of this page"""

        def find_colors(title):
            for adict in color_dict_list:
                if title in adict:
                    return adict[title]
            return []

        # make list guessed_lattice_rows of products in the same order as fixed read to combine them
        index_to_product_rows_guess_lattice = []
        for guessed_df in self.filter_product_dfs(self.__guessed_lattice_dfs):
            # print('guessed_product_df')
            # print(guessed_df)
            guessed_df = guessed_df.fillna('')  # nan fields are substituted by empty string
            guessed_rows = [list(guessed_df.columns), *guessed_df.values.tolist()]

            index_to_product_rows_guess_lattice.append(guessed_rows)

        # For debugging:
        def debug():
            for i, t in enumerate(self.__data_tables):
                print(f"data-table index={i}")
                print(t)
            for ig, gr in enumerate(index_to_product_rows_guess_lattice):
                print(f"guessed rows set index={ig}")
                print(pprint.pformat(gr))

        self.__product_tables = []
        # print('make_product_tables')
        for index, dt in enumerate(self.__data_tables):
            # print(self.__pagenumber)
            try:
                pt = ProductTable(
                    self.__pagenumber,
                    dt,
                    index_to_product_rows_guess_lattice[index],
                    find_colors(dt.title)
                )
                self.__product_tables.append(pt)
            except Exception as e:
                # debug()
                print(f"exception {e}")
                traceback.print_exc()

    def build_tables(self):
        for table in self.__product_tables:
            table.build_table()

    @property
    def product_tables(self):
        return self.__product_tables

    @property
    def color_dict(self):
        return self.__color_dict

    def read_fixed_columns_tabula(self):
        """ :returns df using tabula fixed column recognition"""

        df_list = tabula.read_pdf(
            input_path=self.__infilename,
            output_format="dataframe",
            pages=self.__pagenumber,
            guess=True,
            stream=True,
            multiple_tables=True,
            columns=PFC.COLUMN_X_COORDINATES,
            area=PFC.TABLE_COORDINATES,
            pandas_options={'dtype': str, 'header': None}
        )

        # print("fixed dflist:")
        # self.print_df_list(df_list)

        rows = self.df_to_rows(df_list[0], header=False)
        # print("fixed rows:")
        # for row in rows:
        #     print(row)
        return rows

    # def read_guess_lattice_tabula(self):
    #     # https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html
    #     # # Not doing it with a template
    #     # df_list = tabula.read_pdf_with_template(
    #     #     input_path=self.__infilename,
    #     #     template_path='tabula-3.json'
    #     #     # pages=self.__pagenumber,
    #     #     # guess=True,
    #     #     # lattice=True,
    #     #     # multiple_tables=True,
    #     #     # pandas_options={'dtype': str, 'header': None},
    #     #     # area=PFC.TABLE_COORDINATES
    #     # )
    #
    #     #
    #     df_list = tabula.read_pdf(
    #         input_path=self.__infilename,
    #         pandas_options={'header': None, 'dtype': str},
    #         pages=self.__pagenumber,
    #         lattice=True,
    #         multiple_tables=True,
    #
    #         # area=PFC.TABLE_COORDINATES
    #     )
    #
    #     # self.print_df_list(df_list)
    #
    #     return df_list

    @staticmethod
    def make_data_table_rows(fixed_rows, template_rows):
        """ @:return tuple (data_rows_form_fixed, data_rows_from_template) """

        def is_color_header_in_fixed(r):
            r1 = [str(item) for item in r]
            row_string = "".join(r1)
            if "COLORS" in row_string and not r[0]:
                return True
            return False

        def is_color_header_in_template(r):
            return len(r) == 1 and "COLORS" in r[0]

        def break_into_separate_selections(f_rows):
            tables = []
            cur_table = []
            for row in f_rows:
                if row[-1] == 'Price' or is_color_header_in_fixed(row):
                    if len(cur_table) > 0:
                        tables.append(cur_table)
                    cur_table = [row]
                else:
                    if not len(cur_table) and not row[-1] == 'Price':
                        continue  # skip 1st line of color header with double rows
                    cur_table.append(row)
            tables.append(cur_table)  # append the last table
            return tables

        print("fixed_rows")
        for r in fixed_rows:
            print(r)
        print("template_rows")
        for r_set in template_rows:
            for r in r_set:
                print(r)
            print('-'*10)
        print('\n')

        fixed_result = [t for t in break_into_separate_selections(fixed_rows) if
                        not (is_color_header_in_fixed(t[0]) or is_color_header_in_fixed(t[1]))]
        template_result = []
        for t in template_rows:
            if not (is_color_header_in_template(t[0]) or is_color_header_in_template(t[1])):
                # print("not color header: ", t[0], t[1])
                if "Units/\rCarton" in t[0]:
                    dummy_row = [''] * len(t)
                    t.insert(1, dummy_row)
                template_result.append(t)

        # debug
        print("\nfixed_result:")
        for i, t in enumerate(fixed_result):
            print(f'data table {i}')
            for r2 in t:
                print(r2)

        print("\ntemplate_result:")
        for i, t in enumerate(template_result):
            print(f'data table {i}')
            for r2 in t:
                print(r2)

        result = []
        for index, _ in enumerate(fixed_result):
            result.append((fixed_result[index], template_result[index]))

        return result

    # def
    #
    #     self.print_df_list(df_list)
    #
    #     df = df_list[0]  # the dictionary is on a singleton list
    #     df = df.fillna('')  # nan fields are substituted by empty string
    #
    #     # # for testing
    #     # export_dict_ragged_to_csv(df.to_dict(), self.midfilename)
    #     # convert dataframe to list of rows including header
    #
    #     row_list = [list(df.columns), *df.values.tolist()]
    #
    #     # for row in row_list:
    #     #     print(row)
    #     return row_list

    def read_guess_lattice_table_tabula(self):
        """ :returns list of dfs from pdf using tabula guess and lattice
        used for extracting color tables
        """
        # https://stackoverflow.com/questions/60448160/reading-tables-as-string-from-pdf-with-tabula
        col2str = {'dtype': str}
        kwargs = {'pandas_options': col2str}

        df_list = tabula.read_pdf(
            input_path=self.__infilename,
            # output_format="dataframe",
            pages=self.__pagenumber,
            guess=True,
            lattice=True,
            multiple_tables=True,
            area=PFC.TABLE_COORDINATES,
            **kwargs
        )
        # debugging
        # print("guessed rows:")
        # rows = self.dfs_to_rows(df_list, header=False)
        # for r in rows:
        #     print(r)
        return df_list

    def read_with_json_tabula(self, infilename, pagenumber, json_page_data):
        """
        :return list of lists of rows representing all selections on the current page
        :param json_page_data is a list of dictionaries containing keys: page, extraction_method, x1, x2, y1, y2, width, height
         which is relevant to the current page only"""
        selection_coordinates = [(data["y1"], data["x1"], data["y2"], data["x2"]) for data in
                                 json_page_data]  # list of tuples of $y1,$x1,$y2,$x2 coordinates for this page
        selection_coordinates.sort(key=lambda selection: selection[1])  # sort by x1
        selection_coordinates.sort(key=lambda selection: selection[0])  # sort by y1
        df_list = []  # list of rows representing current page
        # print("read_with_json_tabula:")

        for c_tuple in selection_coordinates:
            df_singleton = tabula.read_pdf(
                input_path=infilename,
                output_format="dataframe",
                pages=pagenumber,
                lattice=True,
                # multiple_tables=True,
                # guess=True,
                area=c_tuple,
                encoding='utf-8',
                pandas_options={'dtype': str, 'header': None}

            )

            try:
                df = df_singleton[0]  # the dictionary is on a singleton list
                df = df.fillna('')  # nan fields are substituted by empty string

                df_list.append(df)
                # print("template rows")

            except IndexError:
                pass
                # print(f"No selections on page {pagenumber}")

        # debugging
        print("tabula.read_pdf with template")
        self.print_df_list(df_list)

        result = [self.df_to_rows(df, header=False) for df in df_list]

        return result

    @staticmethod
    def list_contains_color_table(alist):
        if len(alist[0]) < 4:
            for row in alist:
                for col_index, item in enumerate(row):
                    if "COLORS" in str(item).upper():
                        return True
        return False

    @staticmethod
    def filter_color_dfs(dfs):
        return [df.fillna('') for df in dfs if
                PdfPage.list_contains_color_table([list(df.columns.values), *df.values])]

    @staticmethod
    def filter_product_dfs(dfs):
        return [df.fillna('') for df in dfs if
                not PdfPage.list_contains_color_table([list(df.columns.values), *df.values])]

    @staticmethod
    def print_df_list(df_list):
        # print dataframes of the page
        for (i, df) in enumerate(df_list):
            print(f"dataframe number: {i}")
            print(tabulate(df, headers=df.columns))

    @staticmethod
    def df_to_rows(df, header=True):
        row_list = []

        df = df.fillna('')  # nan fields are substituted by empty string
        df = df.astype(str)
        # convert dataframe to list of rows including header
        if header:
            row_list.extend([list(df.columns), *df.values.tolist()])
        else:
            row_list.extend([*df.values.tolist()])
        return row_list

    def make_color_dict(self):
        def get_key(df):
            """:return (key, key.stripped)"""
            for item in list(df.columns.values):
                if "COLORS" in item.upper():
                    return item, item.replace("COLORS", "").strip(' -\r').replace(" ", "")  # No-spaces-key

        def make_color_list(df):
            key = get_key(df)[0]
            return [" ".join(item.split()) for item in df[key].tolist()]

        result = {}
        for df in self.__color_dfs:
            # print(tabulate(df, headers=df.columns))
            try:
                result[get_key(df)[1]] = make_color_list(df)
            except Exception as e:
                print("get_key(df)")
                print(get_key(df))
                # print(tabulate(df, headers=df.columns))
                traceback.print_exc()
                raise e

        # {get_key(df)[1]: make_color_list(df) for df in self.__color_dfs}
        return result
