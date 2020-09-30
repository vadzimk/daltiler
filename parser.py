import openpyxl
import csv
import tabula
from openpyxl import Workbook
import subprocess

import TEMPLATE
import functions as f  # contains major functions
import PCONST as PC  # contains pdf constants

# do refactor to make a row a custom object with all the methods

infilename = 'test1.pdf'
outfilename = 'output.xlsx'
midfilename = 'out.csv'

currow = 1  # contains the current row in the output file

# wb = openpyxl.load_workbook(filename) # excel file
# sheet = wb[wb.sheetnames[0]]
wb = Workbook()  # create excel workbook
sheet = wb.active  # get active sheet of the workbook

""" create template header """

# complete row 1 - header
for i in range(len(TEMPLATE.HEADER)):
    sheet.cell(row=currow, column=i + 1, value=TEMPLATE.HEADER[i])



# read pdf into data frame
# df = tabula.read_pdf('test5.pdf', stream=True, pages='all')
# print(df)

# convert pdf into csv
# ------------------------- UNCOMMENT THIS CONVERT PDF -----------------------------
tabula.convert_into(infilename, midfilename, output_format='csv', pages='all', stream=True)
# ---------------------------------------------------------

# read the csv file call it csvfile
with open(midfilename, newline='') as csvfile:
    readerObject = csv.reader(csvfile, delimiter=',', quotechar='|')  # returns reader object that is an iterator
    listOfRows = list(readerObject)

    series_name = ""
    group_name = ""
    subgroup_name = ""

    for r in range(len(listOfRows)):
        row_obj = listOfRows[r]  # row_obj is a of class list


        if f.contains_series(row_obj):
            series_name = f.normalize_name(row_obj[0])

        if f.contains_group(row_obj):
            group_name = row_obj[0]

        if f.contains_subgroup(row_obj):
            SUBGROUP_INDEX = 2
            subgroup_name = row_obj[SUBGROUP_INDEX]

        if f.is_valid_row(row_obj):
            currow += 1  # go to the next row of the outfile to process
            externalid = "{}-{:05d}".format(PC.VENDOR_NAME_CODE, (currow-1))  #formatted string
            print(externalid)
            sheet.cell(row=currow, column=1, value=externalid)
            sheet.cell(row=currow, column=4, value=series_name + " " + group_name + " " + subgroup_name)

            # print(len(row_obj), row_obj)
            # print(r, f.contains_series(row_obj), end=" ")

# ---------------- UNCOMMENT THIS SAVE OUTFILE ------------------------
wb.save(outfilename)
# -------------------------------------------------------------------
wb.close()
