import unittest

import yaml

# TODO Move into real config? Make user-configurable?
DATA_FILE = "orgm.dat"
TEST_DATA_FILE = "orgm_test.dat"

class Item(object):

    def __init__(self, title, area="''", tags=[], actions=[], due_date="''", note=""):
        # TODO validate title is a non-zero-length string, throw otherwise
        self.title = title
        # TODO validate a list if not None
        self.area = area
        # TODO validate a list if not None
        self.tags = tags
        # TODO validate a list if not None
        self.actions = actions
        # TODO real date type and validation
        self.due_date = due_date
        self.note = note

    def __str__(self):
        ret = []
        ret.append("- item:")
        ret.append("  - title: " + self.title)
        ret.append("  - area: " + self.area)
        ret.append("  - tags: " + self.tags.__str__())
        ret.append("  - actions: " + self.actions.__str__())
        ret.append("  - due_date: " + self.due_date)
        ret.append("  - note: | ")
        # Add at least one blank indented line or multi-line can fail to load
        ret.append("      ")
        # Now append note lines if there are any
        ret.append(self.note)
        return "\n".join(ret)

    def __repr__(self):
        return self.__str__()

        
class Organizem:

    def __init__(self, data_file):
        self.data_file = data_file
    
    def _load(self):
        f = open(self.data_file)
        self.data = yaml.load(f)
        f.close()
    
    # Just appends item to end of file using Item.__str__()
    # Maybe there is a way to leverage the library more? Making everything
    #  use str() is brittle compared to having objects yaml-ize transparently
    def add_item(self, item):
        f = open(self.data_file, 'a')         
        f.write(item.__str__())
        f.close
    
    # NOTE: Finds *first* matching title
    def find_item_by_title(self, title):
        self._load()
        for item in self.data:            
            item_data = item['item']
            if item_data[0]['title'] == title:
                return item_data
        return None
        
class OrganizemTestCase(unittest.TestCase):
    
    # Helpers
    def _init_test_data_file(self):
        f = open(TEST_DATA_FILE, 'w')
        item = Item("TEST_ITEM")
        f.write(item.__str__())
        f.close()

    # Tests
    def test_init_item(self):
        title = "title"
        item = Item(title)
        self.assertTrue(item != None)
        self.assertTrue(isinstance(item, Item))
        self.assertTrue(item.title == title)

    def test_init_organizem(self):
        self._init_test_data_file()
        orgm = Organizem(TEST_DATA_FILE)
        self.assertTrue(orgm != None)
        self.assertTrue(isinstance(orgm, Organizem))
        self.assertTrue(orgm.data_file == TEST_DATA_FILE)

    def test_add_item(self):
        self._init_test_data_file()
        title = "title"
        item = Item(title)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)
        orgm.find_item_by_title(title)
        self.assertTrue(orgm.find_item_by_title(title))
        
if __name__ == '__main__':
    unittest.main()