#  template filler
from modules2 import TEMPLATE
from modules2.func import *
from modules2.Target import Target
from modules2.Uom import Uom
from modules2 import PROJ_CONST as PR



def create_target_and_uom(
        product_table_path=PR.DOC_PRODUCT_TABLE,
        target_path=PR.DOC_TARGET,
        uom_path=PR.DOC_UOM
):
    source_dict = read_to_dict(product_table_path)
    target_dict = {k: [] for k in TEMPLATE.HEADER}  # to contain target file of the template

    config_dict = read_to_dict(PR.TARGET_CONFIG)

    target = Target(target_dict, config_dict)
    target.fill_target(source_dict)

    uom_dict = {k: [] for k in TEMPLATE.UOM_HEADER}  # to contain uom file data

    uom = Uom(uom_dict)
    uom.fill_uom(target)

    # export_dict(target_dict, PR.DOC_TARGET)  # column sizes must be equal
    export_dict_ragged_to_csv(target_dict, target_path)

    export_dict_ragged_to_csv(uom_dict, uom_path)
    return True
