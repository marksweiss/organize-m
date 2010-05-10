# Possibly overdesign, but we model each type of YAML element we can have in an
#  Item entry with a class, which handles str(), validation and repr() TODO
# So Item can add new Elements just by choosing on of these Element types
class RootElement(object):
    # Root has a label but no value
    def __init__(self, key):
        if not key: key = Elem.ROOT
        self.key = key
    
    def __str__(self):
        # Leading line break to always init a new Element block
        #  validly at the start of a new line
        return "\n\n- %s:" % self.key

# TODO - Validate val can validly convert to str if it's not None
class ChildTextElement(object):
    # Note the default value of literal empty string to be printed
    # This is a convenience if you later want to fill in a value
    def __init__(self, key, val):
        if not val: val = "''"
        self.key = key
        self.val = val
    
    def __str__(self):
        return "  - %s: %s" % (self.key, self.val)

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
        return "  - %s: %s" % (self.key, self.val)

# TODO - Validate val can validly convert to str if it's not None
class ChildMultilineTextElement(object):
  def __init__(self, key, val):
      if not val: val = ""
      self.key = key
      self.val = val
  
  def __str__(self):
      ret = []
      ret.append('  - %s: |' % self.key)
      for line in self.val.split('\n'):
          ret.append('      %s' % line)          
      return "\n".join(ret)


class Elem(object):
    """
        Defines the types of Elements an Item can have.  Also defines their position
        in Items, and provides metod to map an element to its index. This is used by
        Item to map Python objects deserialized from YAML to YAML representation
        and to Items
    """
    
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
    ITEM_INDEXES = {TITLE : 0, AREA : 1, PROJECT : 2, TAGS : 3, 
                    ACTIONS : 4, DUE_DATE : 5, NOTE : 6}

    @staticmethod
    def index(element):  # TODO RENAME elem_index() or get rid of it
        return Elem.ITEM_INDEXES[element]       

        
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
        self._root = RootElement(Elem.ROOT)
        # TODO validate title is a non-zero-length string, throw otherwise
        self._title = ChildTextElement(Elem.TITLE, title)        
        # Now handle all the optional args, using kwargs because we want the 
        #  flexibility to pass any of these, skipping any we don't care about
        #  so it's not the right use for just default args
        area, project, tags, actions, due_date, note = self.__load_elems(kwelements)          
        # Now load element properties, with vals or None returned from __load_elems()
        self._area = ChildTextElement(Elem.AREA, area)
        self._project = ChildTextElement(Elem.PROJECT, project)        
        self._tags = ChildListElement(Elem.TAGS, tags)
        self._actions = ChildListElement(Elem.ACTIONS, actions)
        # TODO real date type and validation - create a new Element type
        self._due_date = ChildTextElement(Elem.DUE_DATE, due_date)
        self._note = ChildMultilineTextElement(Elem.NOTE, note)
    
    @staticmethod
    def init_from_py_item(py_item):
        """Converts Item serialized to Python object form, dicts and lists, to YAML"""
        
        elems = py_item[Elem.ROOT]
        title = elems[Elem.index(Elem.TITLE)][Elem.TITLE]
        area = elems[Elem.index(Elem.AREA)][Elem.AREA]
        project = elems[Elem.index(Elem.PROJECT)][Elem.PROJECT]
        tags = elems[Elem.index(Elem.TAGS)][Elem.TAGS]        
        actions = elems[Elem.index(Elem.ACTIONS)][Elem.ACTIONS]
        due_date = elems[Elem.index(Elem.DUE_DATE)][Elem.DUE_DATE]
        note = elems[Elem.index(Elem.NOTE)][Elem.NOTE]
        return Item(title, area=area, project=project, tags=tags, actions=actions, due_date=due_date, note=note)
    
    def get_elem_val(self, element):
        if element == Elem.TITLE:
            return self.title
        elif element == Elem.AREA:
            return self.area
        elif element == Elem.PROJECT:
            return self.project
        elif element == Elem.TAGS:
            return self.tags
        elif element == Elem.ACTIONS:
            return self.actions
        elif element == Elem.DUE_DATE:
            return self.due_date
        elif element == Elem.NOTE:
            return self.note
    
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

    # For now str() representation is YAML.  Make separate method to make client
    #  code more explicit and allow future change to str() without client code change
    def __str__(self):
        return self._to_yaml()
    
    def __repr__(self):
        """
        Returns form of object matching form produced by PyYaml.#load() when it loads
        the YAML item from the data file. So then PyYaml.#dump(Item.#repr()) produces
        valid YAML string
        """
        item_repr = {}
        elems = []
        elems.append({Elem.TITLE : self.title})
        elems.append({Elem.AREA : self.area})
        elems.append({Elem.PROJECT : self.project})
        elems.append({Elem.TAGS : self.tags})
        elems.append({Elem.ACTIONS : self.actions})
        elems.append({Elem.DUE_DATE : self.due_date})
        elems.append({Elem.NOTE : self.note})
        item_repr[Elem.ROOT] = elems
        return repr(item_repr)
    
    
    def _to_yaml(self):
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

        
        
    def __load_elems(self, kwelements):
      area = None
      project = None
      tags = None
      actions = None
      due_date = None
      note = None        
      elems = kwelements.keys()        
      if Elem.AREA in elems:
          area = kwelements[Elem.AREA]
      if Elem.PROJECT in elems:
          project = kwelements[Elem.PROJECT]
      if Elem.TAGS in elems: 
          tags = kwelements[Elem.TAGS]
      if Elem.ACTIONS in elems: 
          actions = kwelements[Elem.ACTIONS]
      if Elem.DUE_DATE in elems: 
          due_date = kwelements[Elem.DUE_DATE]
      if Elem.NOTE in elems: 
          note = kwelements[Elem.NOTE]
      return area, project, tags, actions, due_date, note
