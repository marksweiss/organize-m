import re

import yaml
from odict import OrderedDict

from orgm_controller_base import ActionArg
from element import Elem
from item import Item
from item_converter import YamlItemConverter


class Conf(object):
    DATA_FILE = 'data_file'
    DATA_FILE_DFLT_PATH = '../orgm.dat'
    BAK_FILE = 'bak_file'
    BAK_FILE_DFLT_PATH = '../orgm_bak.dat'
    CONF_PATH = 'conf/orgm.conf'
    CONF_TEST_PATH = '../conf/orgm.conf'


class Organizem(object):
    """
    Manages an Organizem TODO data file, binding to a data file by name
    and exposing methods that implement the Actions enum-ed above 
    in class Actions.
    """

    # Public API
    
    # Testers, extenders or anyone who wants to use Organizem programatically
    #  can call these public methods directly. Regular usage is from commmand line
    #  which only uses #run_cli()
    def __init__(self, data_file=None, is_unit_testing=False):
        # Flag used by find() and _init_conf(), so must be set here at top of init
        self._is_unit_testing = is_unit_testing

        # Load any previously stored config settings
        self._conf = self._init_conf()
        
        # Value passed as arg overrides configuration
        if data_file:
            self.data_file = data_file
        # If no path passed as arg, config value is used if found
        elif Conf.DATA_FILE in self._conf:
            self.data_file = self._conf[Conf.DATA_FILE]
        # No value passed as arg or previously stored in config, use default
        else:
            self.data_file = Conf.DATA_FILE_DFLT_PATH
            
        if Conf.BAK_FILE in self._conf:
            self.bak_file = self._conf[Conf.BAK_FILE]
        else:
            self.bak_file = Conf.DATA_FILE_DFLT_PATH
    
    def add_item(self, item):        
        with open(self.data_file, 'a') as f:         
            f.write(str(item))
    
    def add_empty(self):
        self.add_item(Item('DUMMY REQUIRED TITLE ELEMENT'))
    
    # NOTE: Finds all matching items, trying to match the element, value passed
    #  in, e.g. TITLE and a title value, PROJECT and a project value, etc.
    # NOTE: element must be one of the "enums" in class Element (other than ROOT)
    # NOTE: Returns list of 0 or more Items
    def find_items(self, element, pattern, use_regex_match=False):
        ret = self._find_or_filter_items(element, pattern, use_regex_match, is_filter=False)        
        if len(ret) == 0 and not self._is_unit_testing:
            print 'No Items found matching Element = %s. Pattern to match = %s' % (element, pattern)
        return ret
        
    def remove_items(self, element, pattern, use_regex_match=False):
        # Call helper with filtering on and filter predicate the pattern passed in
        # Result is we get back (all rows) - (those that match)
        filtered_items = self._find_or_filter_items(element, pattern, use_regex_match, is_filter=True)              
        # Send all the rewrites to the helper to create new data file        
        self._rewrite(filtered_items)
    
    def get_elements(self, element):
        items = self._load()
        # Use set to get unique values only
        ret = set()
        if items is None:
            return ret
        
        for item in items:
            # Skip empty string and empty list, not interesting to return anyway
            val = item[element]  # use Item.__getitem__() for syntactic sugar
            if val and len(val):
                # Handle case of list and string
                if isinstance(val, str):
                    val = [val]
                for v in val:
                    ret.add(v)
        # Now convert the set of unique values to list to sort it for return. 
        # Return contract is is sorted in descending order.
        ret = list(ret)
        ret.sort()
        return ret
    
    # Groups all items by the distinct values in the element passed in, e.g.
    #  groups by all the tags in the file, or projects or areas.
    def get_grouped_items(self, element):
        items = self._load()
        # Use dictionary that keeps keys in sorted order to return items sorted
        #  by the values for the element key that is being used to group the items
        # NOTE: This is 3p module, odict.py
        ret = OrderedDict()
        if items is None:
            return ret

        for item in items:
            group_keys = item[element] # use Item.__getitem__() for syntactic sugar 
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
    # NOTE: with_group_labels=True is used so default behavior is to
    #  include group labels as YAML comments.  But tests can pass False
    #  to bypass this and just test items written correctly.
    def regroup_data_file(self, element, sort_order, with_group_labels=True):
        grouped_items = self.get_grouped_items(element)               
        items = []
        if grouped_items is None:
            return ""
        group_keys = grouped_items.keys()
        group_keys.sort()        
        # If sort_order is DESCENDING, not the default ASCENDING (also the default for List#sort() )
        #  then reverse the group_keys before building grouped display
        if sort_order == ActionArg.DESCENDING:
            group_keys.reverse()        
        for group_key in group_keys:
            # Mark each group in the regrouped file with a group name label
            if with_group_labels:
                label = self.format_group_label(element, group_key)
                items.append(label)
            # Append the list of items for this group
            items.extend(grouped_items[group_key])
        # Pass the Items, regrouped, to be written to data file
        self._rewrite(items)
        # For convenience, testing/debugging pass the same output back to stdout
        return "\n".join([str(item) for item in items])
        
    def backup(self, bak_file=None):
        if not bak_file:
            bak_file = self.bak_file
        self._backup(bak_file)
  
    def setconf(self, conf, value):
        self._set_conf(conf, value)
        
    def format_group_label(self, elem, group_key):
        group_label = ('# %s: %s' % (elem, group_key))
        border = '# ' + ((len(group_label) - 2) * '-')
        label = '\n\n' + border + '\n' + group_label + '\n' + border              
        return label
  
    # Helpers
    
    # Find/Filter/Match Elem Values
    
    # Applies regex match or not, based on flag, and includes matches 
    #  (if is_filter=False) or excludes matches (if is_filter=True)
    def _find_or_filter_items(self, element, pattern, use_regex_match, is_filter):
        ret = []
        # Some patterns are lists, some strings, so make all lists
        if isinstance(pattern, str): pattern = [pattern]
        # pattern is the same every time in loop below, so just make it a set once here
        pattern = set(pattern)
        # Get the item data, and get the element values from each item
        items = self._load()
        elem_vals = [item[element] for item in items] # use Item.__getitem__() for syntactic sugar
        # Set intersection tests each element value against the pattern to match on
        for i, val in enumerate(elem_vals):
            if isinstance(val, str): val = [val]
            val = set(val)
            is_match = False
            # Handle case of simple value comparison vs. predicate comparison for regex
            if not use_regex_match:
                is_match = pattern & val 
            else:
                is_match = self._is_rgx_intersect(pattern, val, element)            
            # Handle logic of filtering elems that match vs. including elems that match            
            if (is_match and not is_filter) or (not is_match and is_filter):
                ret.append(items[i])                  
        return ret
    
    def _is_rgx_intersect(self, pattern, elem_val, element):
        for p in pattern:
            for v in elem_val:
                if self._is_match(p, v, element, use_regex_match=True):
                    return True
        return False
    
    def _is_match(self, pattern, match_val, element, use_regex_match):
        if not use_regex_match:
            return pattern == match_val
        else:
            # Note types can have line breaks and lots of crap.
            # Increase our chances of avoiding trouble by removing line breaks
            if element == Elem.NOTE:
                match_val = match_val.replace('\n', ' ')                 
            try:
                rgx = re.compile(pattern, re.IGNORECASE)
            except:
                print 'EXCEPTION: Illegal regular expression pattern: ' + pattern + '\n'         
            return rgx.search(match_val) != None
 
    # Data File Management
    
    def _load(self):
        items = []
        with open(self.data_file) as f:
            # NOTE: PyYaml returns list/dict hybrid deserialization from YAML, not class Item
            #  objects we want to manipulate throughout our code (to have one standard, clean, OO
            #  representation of an Item).  So we convert her on _load() and then use Items everywhere
            py_items = yaml.load(f)
            if py_items and len(py_items):
                for py_item in py_items:
                    # Convert each item retrieved from the file to a class Item object
                    items.append(YamlItemConverter.convert_to_item(py_item))             
        return items

    # Useful for debugging, though doesn't support any current feature
    def _dump(self):
        with open(self.data_file, 'r') as f:         
            for line in f:
                print line        
    
    def _backup(self, bak_data_file):
        import shutil
        shutil.copyfile(self.data_file, bak_data_file)

    def _rewrite(self, items):
        self._backup(self.bak_file)
        with open(self.data_file, 'w') as f:     
            for item in items:
                f.write(str(item))
                            
    def _set_conf(self, conf, value):
        self._conf[conf] = value
        # Always persist current state to disk. Next call to _init_conf()
        #  must retrieve the latest configuration values
        conf_path = Conf.CONF_PATH
        if self._is_unit_testing:
            conf_path = Conf.CONF_TEST_PATH
        with open(conf_path, 'w') as f:
            f.write(str(self._conf))
    
    def _get_conf(self, conf):
        self._conf = self._init_conf()
        return self._conf[conf]

    def _init_conf(self):
        self._conf = {}
        conf_path = Conf.CONF_PATH
        if self._is_unit_testing:
            conf_path = Conf.CONF_TEST_PATH
        with open(conf_path) as f:
            stored_conf = f.read()
            if stored_conf:
                self._conf = eval(stored_conf)
        return self._conf
