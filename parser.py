import openpyxl
import csv
import tabula
from openpyxl import Workbook
import subprocess


import TEMPLATE
import functions as f  # contains major functions

infilename = 'test315.pdf'
outfilename = 'output.xlsx'
midfilename = 'out.csv'

currow = 1  # contains the current row



# wb = openpyxl.load_workbook(filename) # excel file
# sheet = wb[wb.sheetnames[0]]
wb = Workbook()  # create excel workbook
sheet = wb.active  # get active sheet of the workbook

""" create template header """

# complete row 1 - header
for i in range(len(TEMPLATE.HEADER)):
    sheet.cell(row=currow, column=i + 1, value=TEMPLATE.HEADER[i])

currow += 1  # update current working row after completing the header

# read pdf into data frame
# df = tabula.read_pdf('test5.pdf', stream=True, pages='all')
# print(df)

# convert pdf into csv
tabula.convert_into(infilename, midfilename, output_format='csv', pages='all', stream=True)

# read the csv file call it csvfile
with open(midfilename, newline='') as csvfile:
    readerObject = csv.reader(csvfile, delimiter=',', quotechar='|')  # returns reader object that is an iterator
    listOfRows = list(readerObject)

    seriesName = ""
    groupName = ""

    for r in range(len(listOfRows)):
        rowObj = listOfRows[r]
        contaisSeries = f.detectSeries(rowObj)
        if contaisSeries:
            seriesName = rowObj[0]
        sheet.cell(row=r + currow, column=4, value=seriesName)


        containsGroup = f.detectGroup(rowObj)
        if containsGroup:
            groupName = rowObj[0]
        sheet.cell(row=r + currow, column=5, value=groupName)

wb.save(outfilename)
wb.close()
