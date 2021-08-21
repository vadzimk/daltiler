import traceback

import tabula
from tabulate import tabulate
from modules2 import PDF_CONST as PFC
from modules2.DataTable import DataTable
from modules2.ProductTable import ProductTable
import pprint


class PdfPage:
    """ when page is created it reads the pdf doc at that page in necessary modes """

    def __init__(self, infilename, pagenumber):
        self.__infilename = infilename
        self.__pagenumber = pagenumber
        print("page: ", self.__pagenumber)
        # datatable is a list of rows

        self.__csv_rows = self.read_fixed_columns_tabula()
        self.__data_tables = [DataTable(table) for table in self.make_data_table_rows(self.__csv_rows)]  # contains
        # list of tables with csv rows that the v1 can recognize

        self.__guessed_lattice_dfs = self.read_guess_lattice_table_tabula()

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

        # TODO debugging:
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

        # print("dflist:")
        # self.print_df_list(df_list)

        rows = self.dfs_to_rows(df_list, header=False)
        # print("rows:")
        # for row in rows:
        #     print(row)
        return rows

    def read_guess_lattice_tabula(self):
        # https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html
        # # Not doing it with a template
        # df_list = tabula.read_pdf_with_template(
        #     input_path=self.__infilename,
        #     template_path='tabula-3.json'
        #     # pages=self.__pagenumber,
        #     # guess=True,
        #     # lattice=True,
        #     # multiple_tables=True,
        #     # pandas_options={'dtype': str, 'header': None},
        #     # area=PFC.TABLE_COORDINATES
        # )

        # TODO works with template
        df_list = tabula.read_pdf(
            input_path=self.__infilename,
            pandas_options={'header': None, 'dtype': str},
            pages=self.__pagenumber,
            lattice=True,
            multiple_tables=True,

            # area=PFC.TABLE_COORDINATES
        )

        # self.print_df_list(df_list)

        return df_list

    @staticmethod
    def make_data_table_rows(rows):
        def is_color_header(r):
            r1 = [str(item) for item in r]
            row_string = "".join(r1)
            if "COLORS" in row_string:
                return True
            return False

        tables = []
        cur_table = []
        for row in rows:
            if row[-1] == 'Price' or is_color_header(row):
                if len(cur_table) > 0:
                    tables.append(cur_table)
                cur_table = [row]
            else:
                if not len(cur_table) and not row[-1] == 'Price':
                    continue  # skip 1st line of color header with double rows
                cur_table.append(row)
        tables.append(cur_table)  # append the last table

        result = [t for t in tables if not is_color_header(t[0]) or is_color_header(t[1])]

        # print("\ndata tables:")
        # for i, t in enumerate(result):
        #     print(f'data table {i}')
        #     for r2 in t:
        #         print(r2)
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
        return df_list

    @staticmethod
    def list_contains_substr(alist, substr):
        for row in alist:
            for item in row:
                if substr in str(item).upper():
                    return True
        return False

    @staticmethod
    def filter_color_dfs(dfs):
        return [df.fillna('') for df in dfs if
                PdfPage.list_contains_substr([list(df.columns.values), *df.values], "COLORS")]

    @staticmethod
    def filter_product_dfs(dfs):
        return [df.fillna('') for df in dfs if
                not PdfPage.list_contains_substr([list(df.columns.values), *df.values], "COLORS")]

    @staticmethod
    def print_df_list(df_list):
        # print dataframes of the page
        for (i, df) in enumerate(df_list):
            print(f"dataframe number: {i}")
            print(tabulate(df, headers=df.columns))

    @staticmethod
    def dfs_to_rows(df_list, header=True):
        row_list = []
        if len(df_list) > 0:
            for df in df_list:
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

        return {get_key(df)[1]: make_color_list(df) for df in self.__color_dfs}
