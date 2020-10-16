import PDF_CONST as PFC  # contains pdf constants
from decimal import Decimal
from modules import GROUPS
import inflect
plur = inflect.engine()


class Target:

    def __init__(self, target_dict, config_dict):
        self._dictionary = target_dict
        self._config = config_dict
        self._keys = list(self._dictionary.keys())


    def fill_target(self, source_d):
        """fill values of target dictionary according to business logic"""


        row_count = 1

        for i in range(len(list(source_d.values())[0])):
            """ subscripts of source_d come from PRODUCT_TABLE_FIELDS
             subscripts of _dictionary come from TEMPLATE"""
            externalid = "{}-{:05d}".format(PFC.VENDOR_NAME_CODE, row_count)
            self._dictionary["externalid"].append(externalid)
            self._dictionary["itemId"].append(externalid)

            item_name = source_d["_series_name"][i] + " " + source_d["_group"][i] + " " + source_d["_subgroup"][i]
            self._dictionary["Item Name"].append(item_name)

            item_number_and_name = externalid + " " + item_name
            self._dictionary["Item Number and Name"].append(item_number_and_name)

            vendor_code = source_d["_vendor_code"][i]
            self._dictionary["vendor name code"].append(vendor_code)
            self._dictionary["vendor1_code"].append(vendor_code)
            self._dictionary["vendor2_code"].append(vendor_code)

            item_size = source_d["_item_size"][i]
            self._dictionary["Item Size"].append(item_size)

            item_color = source_d["_item_color"][i]
            self._dictionary["Item Color"].append(item_color)

            displayname = item_name + " " + item_size + " " + item_color + " " + vendor_code
            displayname = " ".join(displayname.split())  # remove multiple spaces
            self._dictionary["displayname"].append(displayname)

            units_per_carton = source_d['_units_per_carton'][i]
            self._dictionary["Sales QTY Per Pack Unit"].append(units_per_carton)

            units_of_measure = source_d["_units_of_measure"][i]
            if units_of_measure == "PC":
                units_of_measure = "EA"
            self._dictionary["salesdescription"].append(units_of_measure)

            sales_packaging_unit = self.set_packaging_unit(item_name)
            self._dictionary["Sales Packaging Unit"].append(sales_packaging_unit)

            unit_price = Decimal(source_d["_unit_price"][i])
            self._dictionary["cost"].append(unit_price)
            self._dictionary["vendor1_purchaseprice"].append(unit_price)
            self._dictionary["vendor2_purchaseprice"].append(unit_price)

            sales_price = 2 * unit_price
            self._dictionary["Price by UOM"].append(sales_price)

            self._dictionary["unitstype"].append(externalid)

            # "stockunits",
            # "purchaseunits",
            # "saleunits",
            if sales_packaging_unit == "BOX":
                self._dictionary["stockunits"].append("SQUARE FEET")
                self._dictionary["purchaseunits"].append("SQUARE FEET")
                self._dictionary["saleunits"].append("BOXES")
            elif sales_packaging_unit == "EACH":
                self._dictionary["stockunits"].append("EACH")
                self._dictionary["purchaseunits"].append("EACH")
                self._dictionary["saleunits"].append("EACH")
            else:
                self._dictionary["stockunits"].append("SHEETS")
                self._dictionary["purchaseunits"].append("SHEETS")
                self._dictionary["saleunits"].append("SHEETS")

            subsidiary = "Elit Tile Consolidated : Elit Tile Corp (LA)|Elit Tile Consolidated : International Tile and Stone Inc. (noho)"
            self._dictionary["subsidiary"].append(subsidiary)

            product_class = self._config["CLASS"][self.config_row_number(item_name)] # field 24
            self._dictionary["Class"].append(product_class)

            vendor1_name = PFC.vendor1_name
            self._dictionary["vendor1_name"].append(vendor1_name)
            self._dictionary["vendor2_name"].append(vendor1_name)

            vendor1_subsidiary = PFC.vendor1_subsidiary
            self._dictionary["vendor1_subsidiary"].append(vendor1_subsidiary)

            vendor2_subsidiary = PFC.vendor2_subsidiary
            self._dictionary["vendor2_subsidiary"].append(vendor2_subsidiary)

            self._dictionary["itemPriceLine1_itemPriceTypeRef"].append("BASE PRICE") # constant for all vendors

            self._dictionary["itemPriceLine1_quantityPricing"].append(0) # constant for all vendors

            self._dictionary["taxSchedule"].append("Taxable")












            row_count+=1


    def set_packaging_unit(self, itemname):
        sales_packaging_unit = "SHEET"  # default
        sales_packaging_unit = self._config["PACK"][self.config_row_number(itemname)]
        return sales_packaging_unit

    def config_row_number(self, itemname):
        row_n = None
        for i in range(len(self._config["NAMES"])):
            name_list = self._config["NAMES"][i].split(sep=',')
            for name in name_list:
                if name in itemname.upper():
                    row_n = i
        return row_n




