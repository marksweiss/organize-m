import re

import yaml
from odict import OrderedDict

from item import Item


# TODO Move into real config? Make user-configurable?
DATA_FILE = "orgm.dat"


# Manages an Organizem TODO data file, binding to a data file by name
#  and supporting add_item() to add new items and find_item() to find existing items        
class Organizem:

    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None
        
    # Just appends item to end of file using Item.__str__()
    # Maybe there is a way to leverage the library to yaml-ize transparently?
    def add_item(self, item):
        with open(self.data_file, 'a') as f:         
            f.write(str(item))
    
    def add_empty(self):
        self.add_item(Item(''))
    
    # NOTE: Finds all matching items, trying to match the element, value passed
    #  in, e.g. TITLE and a title value, PROJECT and a project value, etc.
    # NOTE: element must be one of the "enums" in class Element (other than ROOT)
    # NOTE: Returns the entire item as a Python object (dict/list combo)
    def find_items(self, element, pattern, is_regex_match=False):
        return self._find_or_filter_items(element, pattern, is_regex_match, is_filter=False)
        
    def remove_items(self, element, pattern, is_regex_match=False):
        items = []
        # Call helper with filtering on and filter predicate the pattern passed in
        # Result is we get back (all rows) - (those that match)
        filtered_items = self._find_or_filter_items(element, pattern, is_regex_match, is_filter=True)
        for item in filtered_items:
            item_data = item[Item.Element.ROOT]            
            # Build append items call dynammically from the current data, then eval()                    
            item_call = "items.append(Item('%s', %s='%s', %s='%s', %s=%s, %s=%s, %s='%s', %s='%s'))" % \
              (item_data[Item.Element.item_index(Item.Element.TITLE)][Item.Element.TITLE], 
              Item.Element.AREA, item_data[Item.Element.item_index(Item.Element.AREA)][Item.Element.AREA],
              Item.Element.PROJECT, item_data[Item.Element.item_index(Item.Element.PROJECT)][Item.Element.PROJECT],
              Item.Element.TAGS, item_data[Item.Element.item_index(Item.Element.TAGS)][Item.Element.TAGS],
              Item.Element.ACTIONS, item_data[Item.Element.item_index(Item.Element.ACTIONS)][Item.Element.ACTIONS],
              Item.Element.DUE_DATE, item_data[Item.Element.item_index(Item.Element.DUE_DATE)][Item.Element.DUE_DATE],
              Item.Element.NOTE, item_data[Item.Element.item_index(Item.Element.NOTE)][Item.Element.NOTE])            
            eval(item_call)
        # Send all the rewrites to the helper to create new data file        
        self._rewrite(items)
    
    def get_elements(self, element):
        self.data = self._load()
        ret = []        
        for item in self.data:
            item_data = item[Item.Element.ROOT]
            ret.append(item_data[Item.Element.item_index(element)][element])
        return ret
    
    # Groups all items by the distinct values in the element passed in, e.g.
    #  groups by all the tags in the file, or projects or areas.
    # Returns Py data structure, list of dicts, keys are the group terms and
    #  values are a list of items (which are dict with values a list of dicts,
    #  which are the name/val elements of the item)
    def get_grouped_items(self, element):
        self.data = self._load()
        # Use dictionary that keeps keys in sorted order to return items sorted
        #  by the values for the element key that is being used to group the items
        # NOTE: This is 3p module, odict.py
        ret = OrderedDict()        
        for item in self.data:
            item_data = item[Item.Element.ROOT]
            group_keys = item_data[Item.Element.item_index(element)][element]
            if isinstance(group_keys, str):
                group_keys = [group_keys]
            for group_key in group_keys:
                if group_key not in ret:
                    ret[group_key] = []
                ret[group_key].append(item)        
        return ret
    
    # Groups items as get_grouped_items() does, then backs up the current
    #  data file to [file_name]_bak, writes the grouped items to the file
    #  and also returns them for convenience and testing purposes
    def regroup_data_file(self, element):
        grouped_items = self.get_grouped_items(element)
        items = []
        for group_key in grouped_items.keys():          
            for item in grouped_items[group_key]:
                items.append(item)
        self._rewrite(items)
        ret = []        
        for item in items:
            ret.append(str(item))
        return "\n".join(ret)
        
    def backup(self, bak_data_file=None):
        if not bak_data_file:
            bak_data_file = self.data_file + '_bak'
        self._backup(bak_data_file)
            
    def run_shell_cmd(self, argv):
        pass

    # Helpers
    
    # This is just to avoid code duplication.  Loops over elements and matches predicate
    #  that is matching pattern.  Applies regex match or not, based on flag, and either
    #  includes matches (if is_filter=False) or excludes matches (if is_filter=True).  Used by
    #  both find_items() and remove_items(), with remove_items() having is_filter=True
    def _find_or_filter_items(self, element, pattern, is_regex_match, is_filter):
        self.data = self._load()
        ret = []        
        for item in self.data: 
            item_data = item[Item.Element.ROOT]
            # Child lists of parent list come back as individual ordered dicts 
            #  in a list, one dict for each child name/value pair (child list).  
            #  So to get the one we care about "generically" we need an enum here 
            #  for the index position of the dict that has the key (Element.X) 
            # Get value for the element of interest, handle cases of string and list            
            match_val = item_data[Item.Element.item_index(element)][element]
            # Support case that some elements are str, and some are list
            if isinstance(match_val, str) and self._match(pattern, match_val, element, is_regex_match, is_filter):
                ret.append(item)
            elif isinstance(match_val, list):
                for val in match_val:
                    # Support letting the caller pass a single value (e.g. one tag)
                    #  or a list of values for elements that are list type
                    if isinstance(pattern, list):
                        for p in pattern:
                            if self._match(p, val, element, is_regex_match, is_filter):
                                ret.append(item)
                    elif isinstance(pattern, str):
                        if self._match(pattern, val, element, is_regex_match, is_filter):
                            ret.append(item)
        # If no matches this returns empty list, which evaluates to "False"
        return ret
    
    def _match(self, pattern, string, element, is_regex_match, is_filter):
        if not is_regex_match:
            return ((pattern == string and not is_filter) or 
                    (pattern != string and is_filter))
        else:
            # Note types can have line breaks and lots of crap.
            # Increase our chances of avoiding trouble by removing line breaks
            if element == Item.Element.NOTE:
               string = string.replace('\n', ' ')    
            rgx = re.compile(pattern, re.IGNORECASE)
            return ((rgx.search(string) != None and not is_filter) or 
                    (rgx.search(string) == None and is_filter))
    
    def _load(self):
        with open(self.data_file) as f:
            self.data = yaml.load(f)
        return self.data

    # Useful for debugging, though doesn't support any current feature
    def _dump(self):
        with open(self.data_file, 'r') as f:         
            lines = f.readlines()
            for line in lines:
                print line        

    # Utility and used by regroup_data_file
    def _backup(self, bak_data_file):
        with open(self.data_file, 'r') as fr:
            lines = fr.readlines()
            with open(bak_data_file, 'w') as fw:
                for line in lines:
                    fw.write(line)
            
    def _rewrite(self, items):
        self._backup(self.data_file + '_bak')
        with open(self.data_file, 'w') as f:         
            for item in items:
                f.write(str(item))