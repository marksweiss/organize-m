import unittest
import yaml

# TODO Move into real config? Make user-configurable?
DATA_FILE = "orgm.dat"
TEST_DATA_FILE = "orgm_test.dat"


class Element(object):
    # Don't use this with #Item.find_item()
    ROOT = 'item'   
    # Use these with #Item.find_item()
    TITLE = 'title'
    AREA = 'area'
    PROJECT = 'project'
    TAGS = 'tags'
    ACTIONS = 'actions'
    DUE_DATE = 'due_date'
    NOTE = 'note'
    
    # Child lists of parent list come back as individual ordered dicts 
    #  in a list, one dict for each child name/value pair (child list).  
    #  So to get the one we care about "generically" we need an enum here 
    #  for the index position of the dict that has the key (Element.X) 
    #  passed as the element arg to this function            
    INDEXES = {TITLE : 0, AREA : 1, PROJECT : 2, TAGS : 3, 
               ACTIONS : 4, DUE_DATE : 5, NOTE : 6}
                  
    @staticmethod
    def index(element):
        return Element.INDEXES[element]


# Possibly overdesign, but we model each type of YAML element we can have in an
#  Item entry with a class, which handles str(), validation and repr() TODO
# So Item can add new Elements just by choosing on of these Element types
class RootElement(object):
    # Root has a label but no value
    def __init__(self, key):
        if not key: key = Element.ROOT
        self.key = key
    
    def __str__(self):
        # Leading line break to always init a new Element block
        #  validly at the start of a new line
        return "\n- " + str(self.key) + ":"

# TODO - Validate val can validly convert to str if it's not None
class ChildTextElement(object):
    # Note the default value of literal empty string to be printed
    # This is a convenience if you later want to fill in a value
    def __init__(self, key, val):
        if not val: val = "''"
        self.key = key
        self.val = val
    
    def __str__(self):
        return "  - " + str(self.key) + ": " + str(self.val)

# TODO - Validate val is a List if it's not None
class ChildListElement(object):
    # Note the default value of a literal empty list
    # This is a convenience that indicates in the file to the user that 
    #  this is a list, so hand edits more likely to be valid
    def __init__(self, key, val):
        if not val: val = []
        self.key = key
        self.val = val
    
    def __str__(self):
        return "  - " + str(self.key) + ": " + str(self.val)

# TODO - Validate val can validly convert to str if it's not None
class ChildMultilineTextElement(object):
  def __init__(self, key, val):
      if not val: val = ""
      self.key = key
      self.val = val
  
  def __str__(self):
      return "  - " + str(self.key) + ": | \n    " + str(self.val)


# A single Item in the TODO file, with a root 'item:' element and child
#  elements for each of the TODO fields, title, project, area, tags, actions
#  due_date and notes
# Only title is required and all other args are optional and any or none can
#  be passed as named args (kwargs)
# Values for all elements are available directly as properties
# str() returns the YAML string serialization of the Item
# repr() TODO returns the Item as a dict/list that is what YAML deserializes to
#  so can be converted back to str() by PyYaml  
class Item(object):

    def __init__(self, title, **kwelements):      
        self._root = RootElement(Element.ROOT)
        # TODO validate title is a non-zero-length string, throw otherwise
        self._title = ChildTextElement(Element.TITLE, title)        
        # Now handle all the optional args, using kwargs because we want the 
        #  flexibility to pass any of these, skipping any we don't care about
        #  so it's not the right use for just default args
        area, project, tags, actions, due_date, note = self.__load_elems(kwelements)          
        # Now load element properties, with vals or None returned from __load_elems()
        self._area = ChildTextElement(Element.AREA, area)
        self._project = ChildTextElement(Element.PROJECT, project)        
        self._tags = ChildListElement(Element.TAGS, tags)
        self._actions = ChildListElement(Element.ACTIONS, actions)
        # TODO real date type and validation - create a new Element type
        self._due_date = ChildTextElement(Element.DUE_DATE, due_date)
        self._note = ChildMultilineTextElement(Element.NOTE, note)
    
    # Props so string values for each Element in the Item are directly available
    @property
    def title(self):
        return self._title.val    
    
    @property
    def area(self):
        return self._area.val

    @property
    def project(self):
        return self._project.val
    
    @property
    def tags(self):
        return self._tags.val
    
    @property
    def actions(self):
        return self._actions.val
    
    @property
    def due_date(self):
        return self._due_date.val
    
    @property
    def note(self):
        return self._note.val

    def __str__(self):
        ret = []
        ret.append(str(self._root))
        ret.append(str(self._title))
        ret.append(str(self._area))
        ret.append(str(self._project))
        ret.append(str(self._tags))
        ret.append(str(self._actions))
        ret.append(str(self._due_date))
        ret.append(str(self._note))
        return "\n".join(ret)

    # TODO Make this serialize to dict/list structure as a string 
    #  that will yaml.load() as is and can eval into a python object
    #def __repr__(self):
    #    return self.__str__()

    def __load_elems(self, kwelements):
      area = None
      project = None
      tags = None
      actions = None
      due_date = None
      note = None        
      elems = kwelements.keys()        
      if Element.AREA in elems:
          area = kwelements[Element.AREA]
      if Element.PROJECT in elems:
          project = kwelements[Element.PROJECT]
      if Element.TAGS in elems: 
          tags = kwelements[Element.TAGS]
      if Element.ACTIONS in elems: 
          actions = kwelements[Element.TAGS]
      if Element.DUE_DATE in elems: 
          due_date = kwelements[Element.DUE_DATE]
      if Element.NOTE in elems: 
          note = kwelements[Element.NOTE]
      return area, project, tags, actions, due_date, note

# Manages an Organizem TODO data file, binding to a data file by name
#  and supporting add_item() to add new items and find_item() to find existing items        
class Organizem:

    def __init__(self, data_file):
        self.data_file = data_file
    
    def _load(self):
        with open(self.data_file) as f:
            self.data = yaml.load(f)
    
    # Just appends item to end of file using Item.__str__()
    # Maybe there is a way to leverage the library to yaml-ize transparently?
    def add_item(self, item):
        with open(self.data_file, 'a') as f:         
            f.write(str(item))
    
    # NOTE: Finds *first* matching item, trying to match the element, value passed
    #  in, e.g. TITLE and a title value, PROJECT and a project value, etc.
    # NOTE: element must be one of the "enums" in class Element (other than ROOT)
    # NOTE: Returns the entire item as a Python object (dict/list combo)
    def find_item(self, element, val):
        # TEMP DEBUG
        #with open(self.data_file, 'r') as f:         
        #    lines = f.readlines()
        #    for line in lines:
        #      print line                
        self._load()
        for item in self.data:
            item_data = item[Element.ROOT]
            # Child lists of parent list come back as individual ordered dicts 
            #  in a list, one dict for each child name/value pair (child list).  
            #  So to get the one we care about "generically" we need an enum here 
            #  for the index position of the dict that has the key (Element.X) 
            #  passed as the element arg to this function            
            if item_data[Element.index(element)][element] == val:
                return item_data
        return None


# TDD all the way ... :-)  
class OrganizemTestCase(unittest.TestCase):
    
    # Helpers
    def _init_test_data_file(self):
        with open(TEST_DATA_FILE, 'w') as f:
            item = Item("TEST_ITEM")
            f.write(str(item))

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

    def test_add_item__find_item_by_title(self):
        self._init_test_data_file()
        title = "title"
        item = Item(title)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_item(Element.TITLE, title))

    def test_add_item__find_item_by_area(self):
        self._init_test_data_file()
        title = "title"
        area = "my area"
        item = Item(title, area=area)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_item(Element.AREA, area))

    def test_add_item__find_item_by_project(self):
        self._init_test_data_file()
        title = "title"
        project = "my project"
        item = Item(title, project=project)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_item(Element.PROJECT, project))


if __name__ == '__main__':
    unittest.main()