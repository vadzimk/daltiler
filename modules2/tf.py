#  template filler
from modules import TEMPLATE
from modules.func import *
from modules.Target import Target
from modules.Uom import Uom

def create_target_and_uom():
    source_dict = read_to_dict(PR.DOC_PRODUCT_TABLE)
    target_dict = {k: [] for k in TEMPLATE.HEADER}  # to contain target file of the template

    config_dict = read_to_dict(PR.TARGET_CONFIG)

    target = Target(target_dict, config_dict)
    target.fill_target(source_dict)

    uom_dict = {k: [] for k in TEMPLATE.UOM_HEADER}  # to contain uom file data

    uom = Uom(uom_dict)
    uom.fill_uom(target)

    # export_dict(target_dict, PR.DOC_TARGET)  # column sizes must be equal
    export_dict_ragged_to_csv(target_dict, PR.DOC_TARGET)

    export_dict_ragged_to_csv(uom_dict, PR.DOC_UOM)
