#  template filler
from modules import PROJ_CONST as PR
import TEMPLATE
import csv
import os
from modules.func import *
from modules.Target import Target

source_dict = read_to_dict(PR.DOC_PRODUCT_TABLE)
target_dict = {k: [] for k in TEMPLATE.HEADER}  # to contain target file of the template

config_dict = read_to_dict(PR.TARGET_CONFIG)



target = Target(target_dict, config_dict)
target.fill_target(source_dict)




# export_dict(target_dict, PR.DOC_TARGET)  # column sizes must be equal
export_dict_ragged_to_csv(target_dict, PR.DOC_TARGET)


