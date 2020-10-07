class PageColorTable:
    """ retrieves set of colors to map to each product on the page"""

    def __init__(self, lines, page_number):
        self.colors = []

    def get_list_of_colors(self):
        return self.colors