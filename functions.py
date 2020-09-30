""" contains major functions """
import subprocess
from html.parser import HTMLParser

import PCONST as PC  # contains pdf constants


def contains_series(row):
    return PC.DETECT_SERIES_SET.issubset(set(row))


# if length of row is 1 and the 0th item is not empty string then it contains group name
def contains_group(row):
    contains = False

    if num_blanks(row) == len(row) - 1 and not cell_is_blank(row[0]):
        contains = True

    return contains


# subgroup is like "BULLNOSE"
def contains_subgroup(row):
    contains = False

    # if row has 7 columns and at least 5 of them are not blank (for now)
    if len(row) == max(PC.ITEM_ROW_LEN) and len(row) - num_blanks(row) in PC.ITEM_ROW_LEN:
        contains = True

    return contains


def contains_vendor_code(row):
    contains = False
    # if row has 7 columns and at least 6 of them are not blank (for now)
    if len(row) == max(PC.ITEM_ROW_LEN) and len(row) - num_blanks(row) == 6:
        contains = True

    return contains


def cell_is_blank(cell):
    return cell == '\"\"' or not cell


# counts number of blanks in a given row
def num_blanks(row):
    count_blank = 0
    for i in range(len(row)):
        if cell_is_blank(row[i]):
            count_blank += 1
    return count_blank


# returns true if the row from midfile to be output in the outfile
def is_valid_row(row):
    row_set = set(row)
    is_valid = False
    if len(row)-num_blanks(row) in PC.ITEM_ROW_LEN and PC.DETECT_SERIES_SET.isdisjoint(row_set) and PC.EMPTY_LINE_FLAGS.isdisjoint(
            row_set):
        is_valid = True
    return is_valid


# removes #
def normalize_name(string):
    return string.replace('#', '')


# def detectSubGroup(row):


# def printRow(sheet, rowN):
#     for i in range(len(row)):
#         sheet.cell(row=r + currow, column=i + 1,
#                    value=listOfRows[r][i])  # copy data from csv into excel file in 1-to-1 correspondence


def convert_pdf_to_html(infilename):
    """" convert pdf to html for error checking """
    # https://www.xpdfreader.com/pdftohtml-man.html
    subprocess.run(["pdftohtml", "-q", infilename, "./xpdf"])

    class MyHtmlParser(HTMLParser):
        # def handle_starttag(self, tag, attrs):
        #     print("encountered start tag: ", tag)
        #
        # def handle_endtag(self, tag):
        #     print("Encountered an end tag: ", tag)

        def __init__(self):
            HTMLParser.__init__(self)
            self.pagedatalist = set()  # creates a new empty set to  hold data items from the html

        def handle_data(self, data):  # method that handles data sent to parser
            # print("encountered some data: ", data)  #test for which data it can retrieve
            self.pagedatalist.add(data)  # adds data item to the set for use in error checking algorithm

    parser = MyHtmlParser()

    with open('./xpdf/page1.html', 'r') as file:
        data = file.read().replace('\n', '')
        parser.feed(data)

    print(parser.pagedatalist)  # output the pagedatalist for testing
