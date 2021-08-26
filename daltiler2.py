import os
import pickle
import sys
import time

import tabula

from modules2.PdfDoc import PdfDoc
from modules2 import PROJ_CONST as PR
from modules2.func import *
from modules2.tf import create_target_and_uom

# pl_cache_name = 'cache.pickle'

#
# def export_pages(obj, filename):
#     """ :param dfs: a dictionary {pagenumber: [df1, df2 ...]}"""
#     try:
#         print(f'Writing file "{filename}"...', end='')
#         with open(filename, 'wb') as out_file_pickled:  # OPEN file TO WRITE BYTES
#             pickle.dump(obj, out_file_pickled)
#             print('done!')
#     except:
#         print('error from pickle_dict')
#
#
# def import_pages(filename):
#     try:
#         print(f"opening pickled {filename}")
#         with open(filename, 'rb') as fh:
#             return pickle.load(fh)
#     except Exception:
#         print(f"error opening pickled {filename}")


def main():

    DOC_SELECTIONS_COORDINATES = find_tabula_template_json_filename()
    if not DOC_SELECTIONS_COORDINATES:
        input(f"Press Enter to close this window")
        return

    try:
        cleanup()
        create_project()
    except PermissionError:
        print(f"Access to the project folder denied\nClose applications that might use it and try again")
        return

    args = sys.argv  # get the list of arguments
    infilename = None
    if len(args) == 2:
        infilename = 'Deltile3.pdf'
        if not os.path.exists(infilename) or not os.path.isfile(infilename):
            print(f"Default input file not found")
            infilename = None
    if not infilename:
        infilename = ask_for_filename(args)

    print(f"Chosen file: {infilename}")

    infilename_n_pages = determine_n_pages(infilename)
    print(f"The number of pages in this file is: {infilename_n_pages}")

    page_start = ask_for_starting_page(infilename_n_pages) or 1
    print(f"Chosen starting page: {page_start}")

    n_pages_to_process = ask_for_n_pages(infilename_n_pages, page_start)
    if n_pages_to_process == "ALL":
        n_pages_to_process = infilename_n_pages - page_start + 1
    else:
        n_pages_to_process = n_pages_to_process or 1

    print(f"Chosen number of pages to process: {n_pages_to_process}")

    print(f"Working on {infilename}\nPlease wait....")
    start_time = time.time()

    # price_list = PdfDoc('3.pdf', 1, 3)
    # price_list = PdfDoc('Daltile2.pdf', 1, 1)
    # price_list = PdfDoc('Daltile3.pdf', 1, 187)

    price_list = PdfDoc(
        infilename,
        template_json=DOC_SELECTIONS_COORDINATES,
        page_start=page_start,
        n_pages=n_pages_to_process
    )

    # # ============= option to use cache ============
    # rescan = True
    # if os.path.exists(pl_cache_name):
    #     print(f"Found {pl_cache_name}")
    #     rescan = input(f"Rescan pages? (y/n): ")
    #     if rescan.lower()=='y':
    #         rescan = True
    #     else:
    #         rescan = False
    # # ==============================================
    # if rescan:
    #     price_list.create_pages()
    #     export_pages(price_list, 'cache.pickle')
    # else:
    #     price_list = import_pages(pl_cache_name)
    # print('=======create tables now============')
    # try:
    print(f"Reading pages:")
    price_list.create_pages()
    print(f"For each page: creating product tables...")
    price_list.create_product_tables()
    print(f"Aggregating data from all tables...")
    price_list.construct_cumulative_dict()
    price_list.patch_cumulative_dictionary()
    print(f"Exporting into the file {PR.DOC_PRODUCT_TABLE}")
    # except:
    #     print("Format of this Pdf document is not supported")
    #     return

    try:
        price_list.export_cumulative_dict()
    except PermissionError:
        print(f"Access to {PR.DOC_PRODUCT_TABLE} denied\nClose applications that might use it and try again")
        return

    create_target_uom_files = input(f"\nYou can open product_table.csv now correct and save and close it.\nCreate target.csv, uom.csv (y/n) ? ")

    if create_target_uom_files.lower() == 'y':
        print(f"Creating template file and UOM file...")
        try:
            create_target_and_uom()
        except PermissionError:
            print(
                f"Access to {PR.DOC_UOM} or {PR.DOC_TARGET} denied\nClose applications that might use it and try again")
            input(f"Press Enter to close this window")
            return

    end_time = time.time()
    hours, rem = divmod(end_time - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Task finished.\n"
          f"Time elapsed: {minutes:.0f} min {seconds:.0f} sec\n"
          f"See:\n{PR.DIR_PROJECT}product_table.csv\n"
          f"{PR.DOC_TARGET}\n"
          f"{PR.DOC_UOM}")

    input(f"Press Enter to close this window")


if __name__ == "__main__":
    main()
