""" contains major functions """
import subprocess
from html.parser import HTMLParser

import PCONST as PC


def detectSeries(row):
    return set(PC.LIST_DETECT_SERIES).issubset(set(row))


# if length of row is 1 and the 0th item is not empty sting then it contains group name
def detectGroup(row):
    return len(row) == 1 and not row[0]


# def detectSubGroup(row):


# def printRow(sheet, rowN):
#     for i in range(len(row)):
#         sheet.cell(row=r + currow, column=i + 1,
#                    value=listOfRows[r][i])  # copy data from csv into excel file in 1-to-1 correspondence


def convertPdfToHtml(infilename):
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
