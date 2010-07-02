import re

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

    # Return all the elements used by class Item to construct an Item
    @staticmethod
    def get_elems():
        return Elem.ELEM_LIST

    # Return all data elemements in an Item, so we can treat them as an opaque collection in various places
    #  and just iterate the list of them
    @staticmethod
    def get_data_elems():
        return Elem.ELEM_LIST[1:]

    # Return all optional data elemements in an Item, so Item can iterate and setattr dynamically 
    @staticmethod
    def get_optional_data_elems():
        return Elem.ELEM_LIST[2:]

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
    def elem_init(elem, val):
        # Factory method to construct Elements of the right type
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
