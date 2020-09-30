import tabula

# read pdf into data frame
# df = tabula.read_pdf('test5.pdf', stream=True, pages='all')
# print(df)

tabula.convert_into('PRICEBOOK (Daltile).pdf', 'archive/all.csv', output_format='csv', pages='all', stream=True)