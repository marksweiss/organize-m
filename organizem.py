import re

import yaml
from odict import OrderedDict

from item import Item, Elem


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


# Manages an Organizem TODO data file, binding to a data file by name
#  and supporting add_item() to add new items and find_item() to find existing items        
class Organizem(object):

    # Public API
    # Testers, extenders or anyone who wants to use Organizem programatically
    #  can call these public methods directly. Regular usage is from commmand line
    #  which only uses #run_cli()
    def __init__(self, data_file=DATA_FILE):
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
    # NOTE: Returns the entire item as a Python object (dict/list combo) or None if no matches found
    def find_items(self, element, pattern, is_regex_match=False):
        ret = self._find_or_filter_items(element, pattern, is_regex_match, is_filter=False)
        if ret == [] or ret == '':
            return None        
        return ret
        
    def remove_items(self, element, pattern, is_regex_match=False):
        items = []
        # Call helper with filtering on and filter predicate the pattern passed in
        # Result is we get back (all rows) - (those that match)
        filtered_items = self._find_or_filter_items(element, pattern, is_regex_match, is_filter=True)              
        for item in filtered_items:
            item_data = item[Elem.ROOT]            
            # Build append items call dynammically from the current data, then eval()                    
            item_call = "items.append(Item('%s', %s='%s', %s='%s', %s=%s, %s=%s, %s='%s', %s='%s'))" % \
              (item_data[Elem.index(Elem.TITLE)][Elem.TITLE], 
              Elem.AREA, item_data[Elem.index(Elem.AREA)][Elem.AREA],
              Elem.PROJECT, item_data[Elem.index(Elem.PROJECT)][Elem.PROJECT],
              Elem.TAGS, item_data[Elem.index(Elem.TAGS)][Elem.TAGS],
              Elem.ACTIONS, item_data[Elem.index(Elem.ACTIONS)][Elem.ACTIONS],
              Elem.DUE_DATE, item_data[Elem.index(Elem.DUE_DATE)][Elem.DUE_DATE],
              Elem.NOTE, item_data[Elem.index(Elem.NOTE)][Elem.NOTE])            
            eval(item_call)
        # Send all the rewrites to the helper to create new data file        
        self._rewrite(items)
    
    def get_elements(self, element):
        self.data = self._load()
        ret = []
        if self.data is None:
            return ret
        for item in self.data:
            item_data = item[Elem.ROOT]
            ret.append(item_data[Elem.index(element)][element])
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
        if self.data is None:
            return ret
        for item in self.data:
            item_data = item[Elem.ROOT]
            group_keys = item_data[Elem.index(element)][element]
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
            return items
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
        filename = args.filename
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
            if not len(title):
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
            if items:
                for item in items:              
                    print str(Item.py_item_to_item(item)) + '\n'
        
        # TODO
        elif action == Action.SHOW_GROUPED:
            return self.get_grouped_items(group_elem)
        
        # TODO
        elif action == Action.SHOW_ELEMENTS:
            return self.get_elements(group_elem)
        
        # TODO    
        elif action == Action.REBUILD_GROUPED:
            self.regroup_data_file(group_elem)
            
        # TODO
        elif action == Action.BACKUP:
            self.backup(filename)


    # Helpers
    
    # This is just to avoid code duplication.  Loops over elements and matches predicate
    #  that is matching pattern.  Applies regex match or not, based on flag, and either
    #  includes matches (if is_filter=False) or excludes matches (if is_filter=True).  Used by
    #  both find_items() and remove_items(), with remove_items() having is_filter=True
    def _find_or_filter_items(self, element, pattern, is_regex_match, is_filter):
        self.data = self._load()
        ret = [] 
        if self.data is None:
            return ret        
        for item in self.data: 
            item_elems = item[Elem.ROOT]
            # Child lists of parent list come back as individual ordered dicts 
            #  in a list, one dict for each child name/value pair (child list).  
            #  So to get the one we care about "generically" we need an enum here 
            #  for the index position of the dict that has the key (Element.X) 
            # Get value for the element of interest, handle cases of string and list            
            elem_val = item_elems[Elem.index(element)][element]
            
            # Support case that some elements are str, and some are list
            # These are the match cases:
            # 1) pattern is str, elem_val is str, not is_filter
            # 2) pattern is str, elem_val is str, is_filter
            # 3) pattern is str, elem_val is list, not is_filter
            # 4) pattern is str, elem_val is list, is_filter
            # 5) pattern is list, elem_val is str, not is_filter
            # 6) pattern is list, elem_val is str, is_filter
            # 7) pattern is list, elem_val is list, not is_filter
            # 8) pattern is list, elem_val is list, is_filter
            
            # 1) and 2)
            # Straight match scalar value to scalar value
            if isinstance(pattern, str) and isinstance(elem_val, str):
                is_match = self._is_match(pattern, elem_val, element, is_regex_match)
                # 1)
                if (is_match and not is_filter):
                    ret.append(item)
                # 2)
                elif(not is_match and is_filter):
                    ret.append(item)
            # 3) and 4)
            # Match scalar pattern to any element of elem_val list
            elif isinstance(pattern, str) and isinstance(elem_val, list):
                # Scope outside loop because we only include this item in is_filter case
                #  if we've checked every item and *none* match
                is_match = False
                for v in elem_val:
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
            elif isinstance(pattern, list) and isinstance(elem_val, str):
                is_match = False
                for p in pattern:
                    is_match = self._is_match(p, elem_val, element, is_regex_match)
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
            elif isinstance(pattern, list) and isinstance(elem_val, list):
                is_match = False
                for p in pattern:
                    for v in elem_val:
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