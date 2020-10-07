import os
from pathlib import Path
import shutil

from modules import PROJ_CONST as PR


def cleanup():
    if os.path.exists(PR.DIR_PROJECT) and os.path.isdir(PR.DIR_PROJECT):
        print("Deleting old project flies...")
        shutil.rmtree(PR.DIR_PROJECT)

    if os.path.exists("xpdf") and os.path.isdir("xpdf"):
        print("xpdf exists, deleting it....")
        shutil.rmtree("xpdf")

def create_project():
    print("Creating new project directory")
    # create directory for the project
    Path(PR.DIR_PROJECT).mkdir(parents=False, exist_ok=True)
    Path(PR.DIR_TABULATED_CSV).mkdir(parents=False, exist_ok=True)
    Path(PR.DIR_PRODUCT_TABLES).mkdir(parents=False, exist_ok=True)