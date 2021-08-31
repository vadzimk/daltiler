import re

from modules2 import PDF_CONST as PFC
from decimal import Decimal


# import inflect
# plur = inflect.engine()


class Target:

    def __init__(self, target_dict, config_dict):
        self._dictionary = target_dict
        self._config = config_dict
        self._keys = list(self._dictionary.keys())
        self._packaging_abbreviation = {"BOX": "BX", "EACH": "EA", "SHEET": "SHT", "SQUARE FOOT": "SF"}
        self._units_of_measure_to_sales_packaging_unit = {
            'SF': 'SQUARE FEET',
            'PC': 'EACH',
            'PAC': 'PAC',
            'SH': 'SHEETS',
            'SET': 'SETS',
            'EA': 'EACH',
            'LF': 'LINEAR FEET'
        }
        self._singulars = {
            "SQUARE FEET": "SQUARE FOOT",
            "BOXES": "BOX",
            "EACH": "EACH",
            'PAC': 'PAC',
            "SHEETS": "SHEET",
            'SETS': 'SET',
            'LINEAR FEET': 'LINEAR FOOT'
        }


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
            item_name = " ".join(item_name.split())  # remove double spaces
            self._dictionary["Item Name"].append(item_name.upper())

            config_row_n = self.config_row_number(item_name)  # row number of TARGET_CONFIG

            item_number_and_name = externalid + " " + item_name
            self._dictionary["Item Number and Name"].append(item_number_and_name.upper())

            vendor_code = source_d["_vendor_code"][i]
            self._dictionary["vendor name code"].append(vendor_code)
            self._dictionary["vendor1_code"].append(vendor_code)
            self._dictionary["vendor2_code"].append(vendor_code)

            item_size = source_d["_item_size"][i]

            item_size = re.sub(r'(?<=[0-9]) X (?=[0-9])', r'X', item_size.upper().replace('\"', ''))
            self._dictionary["Item Size"].append(item_size)

            item_color = source_d["_item_color"][i]
            self._dictionary["Item Color"].append(item_color.upper())

            displayname = item_name + " " + item_size + " " + item_color + " " + vendor_code
            displayname = " ".join(displayname.split())  # remove multiple spaces
            displayname = displayname.upper()
            self._dictionary["displayname"].append(displayname)

            units_of_measure = source_d["_units_of_measure"][i]  # not used but might replace sales_unit_abbreviated

            target_config_pack = self.packaging_unit_configued(
                config_row_n)  # looks up in csv file the type of product and determines the sales unit
            units_of_measure_formatted = self._units_of_measure_to_sales_packaging_unit.get(
                units_of_measure, units_of_measure)
            sales_packaging_unit = target_config_pack if target_config_pack else units_of_measure_formatted

            self._dictionary["Sales Packaging Unit"].append(sales_packaging_unit)

            units_per_carton = source_d['_units_per_carton'][i]

            """ salesdescription """

            sales_unit_abbreviated = self._packaging_abbreviation.get(
                self._singulars.get(sales_packaging_unit, sales_packaging_unit), sales_packaging_unit)
            self._dictionary["salesdescription"].append(
                units_per_carton + " " + units_of_measure + "/BX" if not units_of_measure == "PC" else units_per_carton + " EA/BX")

            # "Pcs in a Box",
            # "SQFT BY PCS/SHEET",
            # "SQFT BY BOX",
            if sales_unit_abbreviated == "EA":
                self._dictionary["Pcs in a Box"].append(units_per_carton)
                self._dictionary["SQFT BY PCS/SHEET"].append("")
                self._dictionary["SQFT BY BOX"].append("")
            elif sales_unit_abbreviated == "SHT":
                self._dictionary["Pcs in a Box"].append("")
                self._dictionary["SQFT BY PCS/SHEET"].append(units_per_carton)
                self._dictionary["SQFT BY BOX"].append("")
            elif sales_unit_abbreviated == "BX":
                self._dictionary["Pcs in a Box"].append("")
                self._dictionary["SQFT BY PCS/SHEET"].append("")
                self._dictionary["SQFT BY BOX"].append(units_per_carton)
            else:
                self._dictionary["Pcs in a Box"].append("")
                self._dictionary["SQFT BY PCS/SHEET"].append("")
                self._dictionary["SQFT BY BOX"].append("")

            Sales_QTY_Per_Pack_Unit = 1
            if sales_packaging_unit == "BOX":
                Sales_QTY_Per_Pack_Unit = units_per_carton
            self._dictionary["Sales QTY Per Pack Unit"].append(Sales_QTY_Per_Pack_Unit)

            number_string = source_d["_unit_price"][i]
            unit_price = Decimal(number_string.replace(',', ''))
            self._dictionary["cost"].append(unit_price)
            self._dictionary["vendor1_purchaseprice"].append(unit_price)
            self._dictionary["vendor2_purchaseprice"].append(unit_price)

            sales_price = 2 * unit_price
            self._dictionary["Price by UOM"].append(sales_price)

            self._dictionary["unitstype"].append(externalid)

            # "stockunits",
            # "purchaseunits",
            # "saleunits",
            self._dictionary["stockunits"].append(units_of_measure_formatted)
            self._dictionary["purchaseunits"].append(units_of_measure_formatted)
            self._dictionary["saleunits"].append(sales_packaging_unit)

            # # Old requirements:
            # if sales_packaging_unit == "BOX":
            #     self._dictionary["stockunits"].append("SQUARE FEET")
            #     self._dictionary["purchaseunits"].append("SQUARE FEET")
            #     self._dictionary["saleunits"].append("BOXES")
            # elif sales_packaging_unit == "EACH":
            #     self._dictionary["stockunits"].append("EACH")
            #     self._dictionary["purchaseunits"].append("EACH")
            #     self._dictionary["saleunits"].append("EACH")
            # else:
            #     self._dictionary["stockunits"].append("SHEETS")
            #     self._dictionary["purchaseunits"].append("SHEETS")
            #     self._dictionary["saleunits"].append("SHEETS")

            subsidiary = "Elit Tile Consolidated : Elit Tile Corp (LA)|Elit Tile Consolidated : International Tile and Stone Inc. (noho)"
            self._dictionary["subsidiary"].append(subsidiary)

            if config_row_n:
                product_class = self._config["CLASS"][self.config_row_number(item_name)]  # field 24
            else:
                product_class = "100"
            self._dictionary["Class"].append(product_class)

            vendor1_name = PFC.vendor1_name
            self._dictionary["vendor1_name"].append(vendor1_name)
            self._dictionary["vendor2_name"].append(vendor1_name)

            vendor1_subsidiary = PFC.vendor1_subsidiary
            self._dictionary["vendor1_subsidiary"].append(vendor1_subsidiary)

            vendor2_subsidiary = PFC.vendor2_subsidiary
            self._dictionary["vendor2_subsidiary"].append(vendor2_subsidiary)

            self._dictionary["itemPriceLine1_itemPriceTypeRef"].append("BASE PRICE")  # constant for all vendors

            itemPriceLine1_itemPrice = Decimal(Sales_QTY_Per_Pack_Unit) * Decimal(sales_price)
            self._dictionary["itemPriceLine1_itemPrice"].append(itemPriceLine1_itemPrice)

            self._dictionary["itemPriceLine1_quantityPricing"].append(0)  # constant for all vendors

            self._dictionary["taxSchedule"].append("Taxable")

            self._dictionary["vendor1_preferred"].append("T")

            self._dictionary["vendor2_preferred"].append("T")

            row_count += 1

    def packaging_unit_configued(self, row_n):
        sales_packaging_unit = None # default was "EACH"
        if row_n:
            target_config_pack = self._config["PACK"][row_n]
            sales_packaging_unit = target_config_pack
        return sales_packaging_unit

    def config_row_number(self, itemname):
        """ @:returns row number of TARGET_CONFIG.csv
            @:param itemname is the name to look for in th names column of the TARGET_CONFIG.csv"""
        # print("itemname", itemname)
        row_n = None
        missing_name = ""
        for i in range(len(self._config["NAMES"])):
            name_list = self._config["NAMES"][i].split(sep=',')
            for name in name_list:
                if name in itemname.upper():
                    row_n = i
                missing_name = name
        # print("missing_name", missing_name)
        return row_n
