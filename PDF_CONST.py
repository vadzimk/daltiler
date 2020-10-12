""" contains pdf constants to detect attributes """

ITEM_ROW_LEN = {5, 6, 7}  # number of possible columns in an itemrow
EMPTY_LINE_FLAGS = {"Carton"}
DETECT_SERIES_SET = {"Units/", "U/M", "Price"}
VENDOR_CODE_INDEX = 1  # index of the item of the list that contains vendor code

# EXTERNAL DATA
VENDOR_NAME_CODE = "V006"

PRODUCT_TABLE_FIELDS = [
    "_pagenumber",
    "_series_name",
    "_group",
    "_item_size",
    "_vendor_code",
    "_subgroup",
    "_item_color",
    "_units_per_carton",
    "_units_of_measure",
    "_unit_price"
]

