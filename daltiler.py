import sys
import time
from datetime import date

from modules.PdfDoc import PdfDoc
from modules.func import *
from modules.tf import create_target_and_uom


def main():

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

    # html_created = convert_to_html(infilename, page_start, page_start + n_pages_to_process - 1)
    # print(f"Html files created...\nCreating product tables. Please wait...")

    price_list = PdfDoc(infilename, page_start=page_start, n_pages=n_pages_to_process)
    print(f"Reading pages:")
    price_list.create_pages()
    print(f"For each page: creating product tables...")
    price_list.create_product_tables()
    print(f"Aggregating data from all tables...")
    price_list.construct_cumulative_dict()
    print(f"Exporting into the file {PR.DOC_PRODUCT_TABLE}")

    try:
        price_list.export_cumulative_dict()
    except PermissionError:
        print(f"Access to {PR.DOC_PRODUCT_TABLE} denied\nClose applications that might use it and try again")
        return

    create_target_uom_files = input(f"Create target.csv, uom.csv (y/n) ? ")

    if create_target_uom_files.lower() == 'y':
        print(f"Creating template file and UOM file...")
        try:
            create_target_and_uom()
        except:
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
