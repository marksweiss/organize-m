import yaml

from item import Item


# TODO Move into real config? Make user-configurable?
DATA_FILE = "orgm.dat"

# Manages an Organizem TODO data file, binding to a data file by name
#  and supporting add_item() to add new items and find_item() to find existing items        
class Organizem:

    def __init__(self, data_file):
        self.data_file = data_file
        
    # Just appends item to end of file using Item.__str__()
    # Maybe there is a way to leverage the library to yaml-ize transparently?
    def add_item(self, item):
        with open(self.data_file, 'a') as f:         
            f.write(str(item))
    
    # NOTE: Finds all matching items, trying to match the element, value passed
    #  in, e.g. TITLE and a title value, PROJECT and a project value, etc.
    # NOTE: element must be one of the "enums" in class Element (other than ROOT)
    # NOTE: Returns the entire item as a Python object (dict/list combo)
    def find_items(self, element, val):
        self._load()
        ret = []
        for item in self.data:
            item_data = item[Item.Element.ROOT]
            # Child lists of parent list come back as individual ordered dicts 
            #  in a list, one dict for each child name/value pair (child list).  
            #  So to get the one we care about "generically" we need an enum here 
            #  for the index position of the dict that has the key (Element.X) 
            #  passed as the element arg to this function
            # Get value for the element of interest, handle cases of string and list            
            comp_val = item_data[Item.Element.item_index(element)][element]
            # Support case that some elements are str, and some are list
            if isinstance(comp_val, str) and comp_val == val:
                ret.append(item_data)
            elif isinstance(comp_val, list):
                # Support letting the caller pass a single value (e.g. one tag)
                #  or a list of values for elements that are list type
                if isinstance(val, list):
                    for v in val:
                        if v in comp_val:
                            ret.append(item_data)
                elif isinstance(val, str):
                    if val in comp_val:
                        ret.append(item_data)
        # If no matches this returns empty list, which evaluates to "False"
        return ret
    
    def get_grouped_items(self, element):
        self._load()
        ret = {}        
        for item in self.data:
            item_data = item[Item.Element.ROOT]
            group_keys = item_data[Item.Element.item_index(element)][element]
            if isinstance(group_keys, str):
                group_keys = [group_keys]
            for group_key in group_keys:
                if group_key not in ret:
                    ret[group_key] = []
                ret[group_key].append(item_data)
        return ret
    
    def get_elements(self, element):
        self._load()
        ret = []        
        for item in self.data:
            item_data = item[Item.Element.ROOT]
            ret.append(item_data[Item.Element.item_index(element)][element])
        return ret
    
    # Helpers
    def _load(self):
        with open(self.data_file) as f:
            self.data = yaml.load(f)

    # Useful for debugging, though doesn't support any current feature
    def _dump(self):
        with open(self.data_file, 'r') as f:         
            lines = f.readlines()
            for line in lines:
                print line        
