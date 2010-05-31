import re


class OrganizemIllegalDataFormatException(Exception): pass
class OrganizemIllegalDataTypeException(Exception): pass


class Elem(object):
    """
        Defines the types of Elements an Item can have.  Also defines their position
        in Items, and provides metod to map an element to its index. This is used by
        Item to map Python objects deserialized from YAML to YAML representation
        and to Items
    """
    
    # Element Field Names
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

    # ** Ordered ** list of Element Field Names
    # ** NOTE: this defines format of Items in data file **
    ELEM_LIST = [ROOT, TITLE, AREA, PROJECT, TAGS, ACTIONS, PRIORITY, DUE_DATE, NOTE]

    # Element Class Types
    ROOT_TYPE = 'RootElement'
    TEXT_TYPE = 'ChildTextElement'
    LIST_TYPE = 'ChildListElement'
    MULTILINE_TEXT_TYPE = 'ChildMultilineTextElement'

    ELEM_TYPE_MAP = {ROOT: ROOT_TYPE, 
                     TITLE : TEXT_TYPE, AREA : TEXT_TYPE,
                     PROJECT : TEXT_TYPE, TAGS : LIST_TYPE, 
                     ACTIONS : LIST_TYPE, PRIORITY : TEXT_TYPE, 
                     DUE_DATE : TEXT_TYPE, NOTE : MULTILINE_TEXT_TYPE}

    @staticmethod
    def get_elem_list():
        return Elem.ELEM_LIST
    
    @staticmethod
    def get_optional_elem_list():
        return Elem.ELEM_LIST[2:]

    @staticmethod
    def elem_init(elem, val):
        # Get the type of the element being created, from mapping of elems to types
        # Call that type's __init__() with value for the element, return it
        type = Elem.get_elem_type(elem)
        
        if type == Elem.ROOT_TYPE:
            return RootElement(elem, val)
        elif type == Elem.TEXT_TYPE:
            return ChildTextElement(elem, val)
        elif type == Elem.LIST_TYPE:
            return ChildListElement(elem, val)
        elif type == Elem.MULTILINE_TEXT_TYPE:
            return ChildMultilineTextElement(elem, val)
        else:
             raise OrganizemIllegalDataFormatException("Element %s with value %s is invalid type to conver to str" % (elem, val))

    @staticmethod
    def get_elem_type(elem):
        return Elem.ELEM_TYPE_MAP[elem]
                  
#    @staticmethod
#    def elem_list():
#        return Elem.ELEM_LIST

#    @staticmethod
#    def elem_val_to_str(elem, val):
#        if val is None:
#            return None
#        val = str(val)
#        type = Elem.ELEM_TYPES[elem]
#        if type == 'ChildTextElement':
#            return "'" + val.replace("'", "\\'") + "'"
#        elif type == 'ChildListElement':
#            return val
#        elif type == 'ChildMultilineTextElement':
#            return """%s""" % re.sub(re.compile("'", re.MULTILINE), Elem._repl, val)
#        else:
#            raise OrganizemIllegalDataFormatException("Element %s with value %s is invalid type to conver to str" % (elem, val))

#    @staticmethod
#    def _repl(matchobject):
#        val = matchobject.group(0)
#        if val == "'":
#            return "\\'"
#        else:
#            return val 


class RootElement(object):
    # Root has a label but no value
    def __init__(self, key=None, val=None):
        if not key: key = Elem.ROOT
        self.key = key
        self.val = None
    
    def __str__(self):
        # Leading line break to always init a new Element block
        #  validly at the start of a new line
        return "\n\n- %s:" % self.key

class ChildTextElement(object):
    # Note the default value of literal empty string to be printed
    # This is a convenience if you later want to fill in a value
    def __init__(self, key, val):
        if not val: val = "''"
        self.key = key
        self.val = val
    
    def __str__(self):
        return "  - %s: %s" % (self.key, self.val)

    def escaped_str(self):
        return "'" + str(self.val).replace("'", "\\'") + "'"

class ChildListElement(object):
    # Note the default value of a literal empty list
    # This is a convenience that indicates in the file to the user that 
    #  this is a list, so hand edits more likely to be valid
    def __init__(self, key, val):
        if not val: val = []
        if not isinstance(val, list):
            raise OrganizemIllegalDataTypeException("Illegal value %s for a list element" % val)          
        self.key = key
        self.val = val
    
    def __str__(self):
        return "  - %s: %s" % (self.key, self.val)

    def escaped_str(self):
        return self.val
    
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
    
    def escaped_str(self):
        return """%s""" % \
            re.sub(re.compile("'", re.MULTILINE), ChildMultilineTextElement._repl, self.val)

    @staticmethod
    def _repl(matchobject):
        val = matchobject.group(0)
        if val == "'":
            return "\\'"
        else:
            return val       

# A single Item in the data file, with a root 'item:' element and child
#  elements for each of the fields (Elements) in an Item
# Only title is required and all other args are optional and any or none can
#  be passed as named args (kwargs)
# Values for all elements are available directly as properties
# str() returns the YAML string serialization of the Item
# repr() returns the Item as a dict/list that is what YAML deserializes to
class Item(object):

    def __init__(self, title, **kwelements): 
        # Store list of all elements in Item
        self._elemlist = Elem.get_elem_list()
        
        # Required elements are 'ROOT' and 'TITLE'
        # Set 'root' Item Element
        self.__setattr__('_' + Elem.ROOT, Elem.elem_init(Elem.ROOT, None))           
        # 'title' Element is required, set it first
        if not title:
            raise OrganizemIllegalDataFormatException("Cannot construct Item with null or empty title")
        title_obj = Elem.elem_init(Elem.TITLE, title)
        self.__setattr__('_' + Elem.TITLE, title_obj)
        self.__setattr__(Elem.TITLE, title_obj.val)
                
        # A little dirty, but not bad. Elem exposes method to get list of optional
        #  elements, with the assumption being client can call get_elem_list() to
        #  get all elements and this to get only optional, so it can take care of
        #  required ones (statically, as here) and process optional ones dynamically
        opt_elems = Elem.get_optional_elem_list()        
        for elem in opt_elems:
            kwval = None
            if elem in kwelements:
                kwval = kwelements[elem]
            elem_obj = Elem.elem_init(elem, kwval)
            # Private object str(), repr() used by Item str() and repr()
            self.__setattr__('_' + elem, elem_obj)
            # Public getter just returns obj.val, value for the element
            self.__setattr__(elem, elem_obj.val)

    def __getattr__(self, attr):
        return self.__dict__[attr]
            
    @staticmethod
    def init_from_py_item(py_item):
        """Converts Item serialized to Python object form, dicts and lists, to YAML"""
        
        # The list of names of elements an Item must have for this version
        elem_names = Elem.get_optional_elem_list()
        # List of names of elements in the py_item
        py_elem_names = Item._get_py_item_elem_list(py_item)

        # Item must have title element, so check for that first
        title = Item._get_py_item_title(py_item, py_elem_names)
        
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
                py_elem_val = Elem.elem_init(elem_name, py_elem_val).escaped_str()                
                if py_elem_val:
                    # Handle special case of multiline string value for Note elem
                    # See comment above where note_vals[] is declared
                    if Elem.get_elem_type(elem_name) == Elem.MULTILINE_TEXT_TYPE:
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
        py_elems = py_item[Elem.ROOT]
        num_elems = len(py_elems)
        return [py_elems[j].keys()[0] for j in range(0, num_elems)]

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
                
    def get_elem_val(self, elem):
        return self.__getattr__(elem)
    
    # For now str() representation is YAML.  Make separate method to make client
    #  code more explicit and allow future change to str() without client code change
    def __str__(self):
        return self._to_yaml()
    
    def _to_yaml(self):
        return '\n'.join([str(self.__getattr__('_' + elem)) for elem in self._elemlist])
        
    # NOTE: Used by organizem_test.py unit tests
    def __repr__(self):
        """
        Returns form of object matching form produced by PyYaml.#load() when it loads
        the YAML item from the data file. So then PyYaml.#dump(Item.#repr()) produces
        valid YAML string
        """
        # Use list of elements skipping ROOT
        # Iterate list of elems to create list of dicts, one for each attr
        elems = [{elem : self.__getattr__(elem)} for elem in self._elemlist[1:]]
        item_repr = {Elem.ROOT : elems}
        return repr(item_repr)
