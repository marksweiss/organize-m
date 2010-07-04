from element import Elem


class OrganizemIllegalDataFormatException(Exception): pass
class OrganizemIllegalDataTypeException(Exception): pass


# A single Item in the data file, with a root 'item:' element and child
#  elements for each of the fields (Elements) in an Item
# Only title is required and all other args are optional and any or none can
#  be passed as named args (kwargs)
# Values for all elements are available directly as properties
# str() returns the YAML string serialization of the Item
# repr() returns the Item as a dict/list that is what YAML deserializes to
class Item(object):

    def __init__(self, title, dict_of_elems=None): 
        # Store list of all elements in Item
        self._elems = Elem.get_elems()
        
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
        #  elements, with the assumption being client can call get_optional_data_elems() to
        #  get all elements and this to get only optional, so it can take care of
        #  required ones (statically, as here) and process optional ones dynamically
        opt_elems = Elem.get_optional_data_elems()        
        for elem in opt_elems:
            kwval = None
            elem_obj = None
            if dict_of_elems:
                if elem in dict_of_elems:
                    kwval = dict_of_elems[elem]
                elem_obj = Elem.elem_init(elem, kwval)
                # Private object str(), repr() used by Item str() and repr()
                self.__setattr__('_' + elem, elem_obj)
                # Public getter just returns obj.val, value for the element
                self.__setattr__(elem, elem_obj.val)
            else:
                self.__setattr__('_' + elem, Elem.elem_init(elem, None))
                self.__setattr__(elem, None)
                
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return None
    
    # Used for access to arbitrary element value: x = item[elem]
    def __getitem__(self, elem):
        return self.__getattr__(elem)
    
    # For now str() representation is YAML.  Make separate method to make client
    #  code more explicit and allow future change to str() without client code change
    def __str__(self):
        return self._to_yaml()
    
    def _to_yaml(self):
        return '\n'.join([str(self.__getattr__('_' + elem)) for elem in self._elems])
        
    # NOTE: Used by organizem_test.py unit tests
    def __repr__(self):
        """
        Returns form of object matching form produced by PyYaml.#load() when it loads
        the YAML item from the data file. So then PyYaml.#dump(Item.#repr()) produces
        valid YAML string
        """
        # Use list of elements skipping ROOT
        # Iterate list of elems to create list of dicts, one for each attr
        elems = [{elem : self.__getattr__(elem)} for elem in self._elems[1:]]
        item_repr = {Elem.ROOT : elems}
        return repr(item_repr)
