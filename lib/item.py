import re

class OrganizemIllegalDataFormatException(Exception): pass

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
    PRIORITY = 'priority'
    DUE_DATE = 'due_date'
    NOTE = 'note'

    # ** Ordered ** list of Elements
    # ** NOTE: this defines format of Items in data file **
    ELEM_LIST = [TITLE, AREA, PROJECT, TAGS, ACTIONS, PRIORITY, DUE_DATE, NOTE]

    # Mapping a separate const because Dict doesn't guarantee key order
    ELEM_TYPES = {TITLE : 'ChildTextElement', AREA : 'ChildTextElement',
                  PROJECT : 'ChildTextElement', TAGS : 'ChildListElement', 
                  ACTIONS : 'ChildListElement', PRIORITY : 'ChildTextElement', 
                  DUE_DATE : 'ChildTextElement', NOTE : 'ChildMultilineTextElement'}
    
    @staticmethod
    def elem_list():
        return Elem.ELEM_LIST
    
    @staticmethod
    def _repl(matchobject):
        val = matchobject.group(0)
        if val == "'":
            return "\\'"
        else:
            return val 
        
    @staticmethod
    def elem_val_to_str(elem, val):
        if val is None:
            return None
        val = str(val)
        type = Elem.ELEM_TYPES[elem]
        if type == 'ChildTextElement':
            return "'" + val.replace("'", "\\'") + "'"
        elif type == 'ChildListElement':
            return val
        elif type == 'ChildMultilineTextElement':
            return """%s""" % re.sub(re.compile("'", re.MULTILINE), Elem._repl, val)
        else:
            raise OrganizemIllegalDataFormatException("Element %s with value %s is invalid type to conver to str" % (elem, val))

    # Child lists of parent list come back as individual ordered dicts 
    #  in a list, one dict for each child name/value pair (child list).
    # This lets Item client code not care. ITEM_LIST defines order/data format.             
    @staticmethod
    def _elem_index(elem):
        return Elem.ELEM_LIST.index(elem)       

    @staticmethod
    def _elem_type(elem):
        return Elem.ELEM_TYPES[elem]

            
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

    # TODO MAKE THIS DYNAMIC WITH SETATTR
    def __init__(self, title, **kwelements):      
        self._root = RootElement(Elem.ROOT)
        # TODO validate title is a non-zero-length string, throw otherwise
        self._title = ChildTextElement(Elem.TITLE, title)        
        # Now handle all the optional args, using kwargs because we want the 
        #  flexibility to pass any of these, skipping any we don't care about
        #  so it's not the right use for just default args
        area, project, tags, actions, priority, due_date, note = \
            self.__load_elems(kwelements)          
        # Now load element properties, with vals or None returned from __load_elems()
        self._area = ChildTextElement(Elem.AREA, area)
        self._project = ChildTextElement(Elem.PROJECT, project)        
        self._tags = ChildListElement(Elem.TAGS, tags)
        self._actions = ChildListElement(Elem.ACTIONS, actions)
        self._priority = ChildTextElement(Elem.PRIORITY, priority)
        # TODO real date type and validation - create a new Element type
        self._due_date = ChildTextElement(Elem.DUE_DATE, due_date)
        self._note = ChildMultilineTextElement(Elem.NOTE, note)
    
    @staticmethod
    def init_from_py_item(py_item):
        """Converts Item serialized to Python object form, dicts and lists, to YAML"""
        
        # The list of names of elements an Item must have for this version
        elem_names = Elem.elem_list()
        # List of names of elements in the py_item
        py_elem_names = Item._get_py_item_elem_list(py_item)

        # Item must have title element, so check for that first
        title = Item._get_py_item_title(py_item, py_elem_names)
        # Now reset elem_names to skip TITLE
        elem_names = elem_names[1:]
        
        # Handling dynamic list of kwargs to __init__(), so build string
        #  dynamically and make __init__() call an eval()
        init_call = []
        init_call.append('Item(title')
        # eval(x) where x is a multiline string literal fails on
        #  exception from scanning literal and finding an EOL in it
        # So, store the multiline string in this local List.  Put the
        #  note_vals[idx] into the string to be evaled.
        # And, yes, this is a pretty sweet hack
        note_vals = []                
        # Algo:
        #  - Iterate the list of expected elements, item_elems
        #  - Test for matching elem in py_item passed in (which was loaded from data)
        #  - If found, add to kwargs list with py_item value for Item.__init__()
        #  - If not found, add to kwargs list with None value for Item.__init__()
        for elem_name in elem_names:
            if elem_name in py_elem_names:
                idx = py_elem_names.index(elem_name)
                py_elems = py_item[Elem.ROOT]
                py_elem_val = py_elems[idx][elem_name]
                py_elem_val = Elem.elem_val_to_str(elem_name, py_elem_val)                
                if py_elem_val:
                    # Handle special case of multiline string value for Note elem
                    # See comment above where note_vals[] is declared
                    if elem_name == Elem.NOTE:
                        note_vals.append(py_elem_val)
                        val_idx = len(note_vals) - 1
                        init_call.append(', %s=note_vals[%i]' % (elem_name, val_idx))
                    else:
                        init_call.append(', %s=%s' % (elem_name, py_elem_val))
                else:
                    init_call.append(', %s=None' % elem_name)
            else:
                init_call.append(', %s=None' % elem_name)
        init_call.append(')')
        init_call = ''.join(init_call)
        
        item = eval(init_call)
        return item
    
    @staticmethod
    def _get_py_item_elem_list(py_item):
        elems = py_item[Elem.ROOT]
        num_elems = len(elems)
        return [elems[j].keys()[0] for j in range(0, num_elems)]

    @staticmethod
    def _get_py_item_title(py_item, py_elem_names):
        # Elements in the py_item
        py_elems = py_item[Elem.ROOT]                
        if Elem.TITLE not in py_elem_names:
            raise OrganizemIllegalDataFormatException("Attempted to load Item from data file without required 'title' element")
        idx = py_elem_names.index(Elem.TITLE)
        title = py_elems[idx][Elem.TITLE]
        if not title:
            raise OrganizemIllegalDataFormatException("Attempted to load Item from data file without value for required 'title' element")
        return title
                
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
        elif element == Elem.PRIORITY:
            return self.priority
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
    def priority(self):
        return self._priority.val

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
    
    def _to_yaml(self):
        ret = []
        ret.append(str(self._root))
        ret.append(str(self._title))
        ret.append(str(self._area))
        ret.append(str(self._project))
        ret.append(str(self._tags))
        ret.append(str(self._actions))
        ret.append(str(self._priority))        
        ret.append(str(self._due_date))
        ret.append(str(self._note))
        return '\n'.join(ret)
        
    def __load_elems(self, kwelements):
      area = None
      project = None
      tags = None
      actions = None
      priority = None
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
      if Elem.PRIORITY in elems: 
          priority = kwelements[Elem.PRIORITY]
      if Elem.DUE_DATE in elems: 
          due_date = kwelements[Elem.DUE_DATE]
      if Elem.NOTE in elems: 
          note = kwelements[Elem.NOTE]
      return area, project, tags, actions, priority, due_date, note

    # NOTE: Used by organizem_test.py unit tests
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
        elems.append({Elem.PRIORITY : self.priority})
        elems.append({Elem.DUE_DATE : self.due_date})
        elems.append({Elem.NOTE : self.note})
        item_repr[Elem.ROOT] = elems
        return repr(item_repr)
