import os
import pickle

from modules2.PdfDoc import PdfDoc
from modules2 import PROJ_CONST as PR


def export_pages(obj, filename):
    """ :param dfs: a dictionary {pagenumber: [df1, df2 ...]}"""
    try:
        print(f'Writing file "{filename}"...', end='')
        with open(filename, 'wb') as out_file_pickled:  # OPEN file TO WRITE BYTES
            pickle.dump(obj, out_file_pickled)
            print('done!')
    except:
        print('error from pickle_dict')

pl_cache_name='cache.pickle'

def import_pages(filename):
    try:
        print(f"opening pickled {filename}")
        with open(filename, 'rb') as fh:
            return pickle.load(fh)
    except Exception:
        print(f"error opening pickled {filename}")


def main():
    # price_list = PdfDoc('3.pdf', 1, 3)
    # price_list = PdfDoc('Daltile2.pdf', 1, 1)
    price_list = PdfDoc('Daltile3.pdf', 1, 187)
    # price_list = PdfDoc('Daltile3.pdf', 176, 11)
    # ============= option to use cache ============
    rescan = True
    if os.path.exists(pl_cache_name):
        print(f"Found {pl_cache_name}")
        rescan = input(f"Rescan pages? (y/n): ")
        if rescan.lower()=='y':
            rescan = True
        else:
            rescan = False
    # ==============================================
    if rescan:
        price_list.create_pages()
        export_pages(price_list, 'cache.pickle')
    else:
        price_list = import_pages(pl_cache_name)
    print('=======create tables now============')
    price_list.create_product_tables()
    price_list.construct_cumulative_dict()

    try:
        price_list.export_cumulative_dict()
    except PermissionError:
        print(f"Access to {PR.DOC_PRODUCT_TABLE} denied\nClose applications that might use it and try again")
        return



if __name__ == "__main__":
    main()