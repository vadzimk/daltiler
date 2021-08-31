# import inflect
# plur = inflect.engine()

class Uom:
    def __init__(self, uom_dict):
        self._dictionary = uom_dict

        self._singulars = {"SQUARE FEET": "SQUARE FOOT", "BOXES": "BOX", "EACH": "EACH", "SHEETS": "SHEET"}


    def fill_uom(self, target_obj):
        row_count = 1

        for i in range(len(list(target_obj._dictionary.values())[0])):
            uom_set = {target_obj._dictionary["stockunits"][i], target_obj._dictionary["purchaseunits"][i],
                       target_obj._dictionary["saleunits"][i]}


            for item in uom_set:
                self._dictionary["Item(Type Name)"].append(target_obj._dictionary["externalid"][i])
                self._dictionary["Internal ID *Update Only"].append("")


                u_singular = self._singulars.get(item, "")
                self._dictionary["Unit Name (Name)"].append(u_singular)

                self._dictionary["Plural Name"].append(item)


                abbr = target_obj._packaging_abbreviation.get(u_singular,"")
                self._dictionary["Abbreviation"].append(abbr)

                pl_abbr = ""
                if abbr:
                    pl_abbr = "EA" if abbr=="EA" else abbr + "S"
                self._dictionary["Plural Abbreviation"].append(pl_abbr)



                #               "Conversion Rate(/Base)",
                #               "Base Unit",
                conversion_rate = 1
                base_unit = "Yes"
                if "BOXES" in uom_set and "SQUARE FEET" in uom_set:
                    if u_singular == "BOX":
                        base_unit = "No"
                        conversion_rate = target_obj._dictionary["salesdescription"][i].split()[0]

                self._dictionary["Conversion Rate(/Base)"].append(conversion_rate)

                self._dictionary["Base Unit"].append(base_unit)



                self._dictionary["___for_displayname"].append(target_obj._dictionary["displayname"][i])
                self._dictionary["___salesdescription"].append(target_obj._dictionary["salesdescription"][i])
                self._dictionary["___uom_set"].append(uom_set)


