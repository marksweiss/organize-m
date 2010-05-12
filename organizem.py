import re

import yaml
from odict import OrderedDict

from item import Elem, Item


# TODO Move into real config? Make user-configurable?
DATA_FILE = "orgm.dat"


class OrganizemIllegalUsageException(Exception): pass


class Action(object):
    ADD = 'add'
    ADD_EMPTY = 'add_empty'
    REMOVE = 'remove'
    FIND = 'find'
    SHOW_GROUPED = 'show_grouped'
    SHOW_ELEMENTS = 'show_elements'
    REBUILD_GROUPED = 'rebuild_grouped'
    BACKUP = 'backup'

class ActionArg(object):
    REGEX = 'regex'
    FILENAME = 'filename'
    BY_TITLE = 'by_title'
    BY_AREA = 'by_area'
    BY_PROJECT = 'by_project'
    BY_TAGS = 'by_tags'
    BY_ACTIONS = 'by_actions'


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
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.data = []
        
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
    # NOTE: Returns list of 0 or more Items
    def find_items(self, element, pattern, is_regex_match=False):
        return self._find_or_filter_items(element, pattern, is_regex_match, is_filter=False)
        
    def remove_items(self, element, pattern, is_regex_match=False):
        # Call helper with filtering on and filter predicate the pattern passed in
        # Result is we get back (all rows) - (those that match)
        filtered_items = self._find_or_filter_items(element, pattern, is_regex_match, is_filter=True)              
        # Send all the rewrites to the helper to create new data file        
        self._rewrite(filtered_items)
    
    def get_elements(self, element):
        self.data = self._load()
        # Use set to get unique values only
        ret = set()
        if self.data is None:
            return ret
        
        for item in self.data:
            # Skip empty string and empty list, not interesting to return anyway
            # Handle case of list elements, loop over those to get their values
            val = item.get_elem_val(element)
            if val and len(val):
                if isinstance(val, str):
                    ret.add(val)
                elif isinstance(val, list):
                    for v in val:
                        ret.add(v)
        # Now convert the set of uniqe values to list to sort it for return. Return contract is
        #  is sorted in descending order.
        ret = list(ret)
        ret.sort()
        return ret
    
    # Groups all items by the distinct values in the element passed in, e.g.
    #  groups by all the tags in the file, or projects or areas.
    def get_grouped_items(self, element):
        self.data = self._load()
        # Use dictionary that keeps keys in sorted order to return items sorted
        #  by the values for the element key that is being used to group the items
        # NOTE: This is 3p module, odict.py
        ret = OrderedDict()
        if self.data is None:
            return ret

        for item in self.data:
            group_keys = item.get_elem_val(element)            
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
        if grouped_items is None:
            return ""
        for group_key in grouped_items.keys():
            items.extend(grouped_items[group_key])
        # Pass the Items, regrouped, to be written to data file
        self._rewrite(items)
        # For conveninence, testing/debugging pass the same output back to stdout
        return "\n".join([str(item) for item in items])
        
    def backup(self, bak_data_file=None):
        if not bak_data_file:
            bak_data_file = self.data_file + '_bak'
        self._backup(bak_data_file)
    
    # CLI API
    # Command line users use only this call, indirectly, by passing command lines
    #  to orgm.py#__main__()     
    def run_cli(self, title, args):  
        # Get the action to be taken
        action = args.action
        # Get the mandatory title Element
        title = args.title
        # Get any optional Element values
        area = args.area
        project = args.project
        # Must split() the two list element types, so the string becomes Py list
        tags = args.tags.split(',')
        actions = args.actions.split(',')
        due_date = args.due_date
        note = args.note
        # Get optional Modifiers, regex, filename
        is_regex_match = args.regex
        # Trim single- or double-quotes from filename -- annoying to have this in name
        #  but CLI everywhere else has quotes around args, so this means user
        #  doesn't need to remember to do that
        filename = args.filename
        if filename and len(filename):
            first_char = filename[0]
            # TODO This is obviously flimsy (can have different style quote at each end)
            last_char = filename[len(filename) - 1]
            if ((first_char == "'" or first_char == '"') and \
                (last_char == "'" or last_char == '"')):
                filename = filename[1:-1]
        # group_by_* Modifiers
        # Required for --show_grouped, --rebuild_grouped, --show_elements
        # TODO add validation
        by_title = args.by_title 
        by_area = args.by_area 
        by_project = args.by_project 
        by_tags = args.by_tags 
        by_actions = args.by_actions 
        
        # For actions matching on an element value, figure out which one
        # NOTE: Just uses first one that by usine if/elif.  DOES NOT
        #  validate only one was passed in and raise Exception
        match_elem = None
        match_val = None        
        if action == Action.FIND or action == Action.REMOVE:
            if len(title):
                match_elem = Elem.TITLE
                match_val = title
            elif len(tags):
                match_elem = Elem.TAGS
                match_val = tags                
            elif len(actions):
                match_elem = Elem.ACTIONS
                match_val = actions            
            elif len(note):
                match_elem = Elem.NOTE
                match_val = note
                
        # For actions modified by a group_by arg, figure out which one
        group_elem = None
        if action == Action.SHOW_GROUPED or \
            action == Action.REBUILD_GROUPED or \
            action == Action.SHOW_ELEMENTS:
            if by_title:
                group_elem = Elem.TITLE
            elif by_area:
                group_elem = Elem.AREA
            elif by_project:
                group_elem = Elem.PROJECT
            elif by_tags:
                group_elem = Elem.TAGS
            elif by_actions:
                group_elem = Elem.ACTIONS

        # Now turn cmd line action and arguments into Organizem API call
        if action == Action.ADD:
            if len(title) == 0:
                raise OrganizemIllegalUsageException("'--add' action must include '--title' element and a value for title.")
            item = Item(title, \
                area=area, project=project, tags=tags, \
                actions=actions, due_date=due_date, \
                note=note)
            self.add_item(item)
            
        elif action == Action.ADD_EMPTY:
            self.add_empty()
        
        elif action == Action.REMOVE:
            self.remove_items(match_elem, match_val, is_regex_match)            

        elif action == Action.FIND:
            items = self.find_items(match_elem, match_val, is_regex_match)            
            for item in items:              
                print str(item)
        
        elif action == Action.SHOW_GROUPED:
            grouped_items = self.get_grouped_items(group_elem)            
            group_keys = grouped_items.keys()
            group_keys.sort()
            for group_key in group_keys:
                print '\n\n*** ' + group_key + ' ***'
                for item in grouped_items[group_key]:                    
                    print str(item)
        
        elif action == Action.SHOW_ELEMENTS:
            elems = self.get_elements(group_elem)
            elems.sort()
            for elem in elems:              
                print elem
                    
        elif action == Action.REBUILD_GROUPED:
            self.regroup_data_file(group_elem)
            
        elif action == Action.BACKUP:
            self.backup(filename)


    # Helpers
    
    # This is just to avoid code duplication.  Loops over elements and matches predicate
    #  that is matching pattern.  Applies regex match or not, based on flag, and either
    #  includes matches (if is_filter=False) or excludes matches (if is_filter=True).  Used by
    #  both find_items() and remove_items(), with remove_items() having is_filter=True
    def _find_or_filter_items(self, element, pattern, is_regex_match, is_filter):
        ret = []
        self.data = self._load()
        for item in self.data: 
            match_val = item.get_elem_val(element)

            # Support case that some elements are str, and some are list
            # These are the match cases:
            # 1) pattern is str, match_val is str, not is_filter
            # 2) pattern is str, match_val is str, is_filter
            # 3) pattern is str, match_val is list, not is_filter
            # 4) pattern is str, match_val is list, is_filter
            # 5) pattern is list, match_val is str, not is_filter
            # 6) pattern is list, match_val is str, is_filter
            # 7) pattern is list, match_val is list, not is_filter
            # 8) pattern is list, match_val is list, is_filter
            
            # 1) and 2)
            # Straight match scalar value to scalar value
            if isinstance(pattern, str) and isinstance(match_val, str):
                is_match = self._is_match(pattern, match_val, element, is_regex_match)
                # 1)
                if (is_match and not is_filter):
                    ret.append(item)
                # 2)
                elif(not is_match and is_filter):
                    ret.append(item)
            # 3) and 4)
            # Match scalar pattern to any element of elem_val list
            elif isinstance(pattern, str) and isinstance(match_val, list):
                # Scope outside loop because we only include this item in is_filter case
                #  if we've checked every item and *none* match
                is_match = False
                for v in match_val:
                    is_match = self._is_match(pattern, v, element, is_regex_match)
                     # 3)
                     # Matched and we aren't filtering, so first match means we can short-circuit
                    if (is_match and not is_filter):
                        ret.append(item)
                        break
                # 4)
                # Filtering, we checked every val in elem_val and none matched pattern, so include item
                if is_filter and not is_match:
                    ret.append(item)
            # 5) and 6)
            # Match any element in list pattern to scalar elem_val
            elif isinstance(pattern, list) and isinstance(match_val, str):
                is_match = False
                for p in pattern:
                    is_match = self._is_match(p, match_val, element, is_regex_match)
                     # 5)
                     # Matched and we aren't filtering, so first match means we can short-circuit
                    if (is_match and not is_filter):
                        ret.append(item)
                        break
                # 6)
                # Filtering, we checked every p in pattern and none matched elem_val, so include item
                if is_filter and not is_match:
                    ret.append(item)                        
            # 7) and 8)
            # Match any element in list pattern to any elmentn in list elem_val
            elif isinstance(pattern, list) and isinstance(match_val, list):
                is_match = False
                for p in pattern:
                    for v in match_val:
                        is_match = self._is_match(p, v, element, is_regex_match)
                        # 7)
                        # Matched and we aren't filtering, so first match means we can short-circuit
                        if (is_match and not is_filter):
                            ret.append(item)
                            break
                    # Now break out of outer loop in case of match and not filter, second short-circuit
                    if (is_match and not is_filter):
                        break
                # 8)
                # Filtering, we checked every p in pattern and none matched elem_val, so include item
                if is_filter and not is_match:
                    ret.append(item)
        # If no matches this returns empty list, which evaluates to "False"
        return ret
            
    def _is_match(self, pattern, match_val, element, is_regex_match):
        if not is_regex_match:
            return pattern == match_val
        else:
            # Note types can have line breaks and lots of crap.
            # Increase our chances of avoiding trouble by removing line breaks
            if element == Elem.NOTE:
               match_val = match_val.replace('\n', ' ')    
            rgx = re.compile(pattern, re.IGNORECASE)
            return rgx.search(match_val) != None
    
    def _load(self):
        with open(self.data_file) as f:
            # NOTE: PyYaml returns list/dict hybrid deserialization from YAML, not class Item
            #  objects we want to manipulate throughout our code (to have one standard, clean, OO
            #  representation of an Item).  So we convert her on _load() and then use Items everywhere
            py_items = yaml.load(f)
            if py_items and len(py_items):
                # We got back to data to load, clear any previous state in self.data
                del self.data[:]
                for py_item in py_items:
                    # Convert each item retrieved from the file to a class Item object
                    self.data.append(Item.init_from_py_item(py_item))             
        return self.data

    # Useful for debugging, though doesn't support any current feature
    def _dump(self):
        with open(self.data_file, 'r') as f:         
            for line in f:
                print line        
    
    def _backup(self, bak_data_file):
  	    import shutil
  	    shutil.copyfile(self.data_file, bak_data_file)

    def _rewrite(self, items):
        self._backup(self.data_file + '_bak')
        with open(self.data_file, 'w') as f:     
            for item in items:
                f.write(str(item))
