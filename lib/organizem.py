import re

import yaml
from odict import OrderedDict

from element import Elem
from item import Item
from item_converter import YamlItemConverter


class OrganizemIllegalUsageException(Exception): pass


class Conf(object):
    DATA_FILE = 'data_file'
    DATA_FILE_DFLT_PATH = '../orgm.dat'
    BAK_FILE = 'bak_file'
    BAK_FILE_DFLT_PATH = '../orgm_bak.dat'
    CONF_PATH = 'conf/orgm.conf'
    CONF_TEST_PATH = '../conf/orgm.conf'

class Action(object):
    ADD = 'add'
    ADD_EMPTY = 'add_empty'
    REMOVE = 'remove'
    FIND = 'find'
    SHOW_GROUPED = 'show_grouped'
    SHOW_ELEMENTS = 'show_elements'
    REBUILD_GROUPED = 'rebuild_grouped'
    BACKUP = 'backup'
    SETCONF_DATA_FILE = 'setconf_data_file'
    SETCONF_BAK_FILE = 'setconf_bak_file'

class ActionArg(object):
    REGEX = 'regex'
    FILENAME = 'filename'
    BY_TITLE = 'by_title'
    BY_AREA = 'by_area'
    BY_PROJECT = 'by_project'
    BY_TAGS = 'by_tags'
    BY_ACTIONS = 'by_actions'
    BY_PRIORITY = 'by_priority'


class Organizem(object):
    """
    Manages an Organizem TODO data file, binding to a data file by name
    and exposing methods that implement the Actions enum-ed above 
    in class Actions.
    """

    ############
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
    
    # Just appends item to end of file using Item.__str__()
    # Maybe there is a way to leverage the library to yaml-ize transparently?
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
            val = item.get_elem_val(element)
            if val and len(val):
                # Handle case of list and string
                if isinstance(val, str):
                    val = [val]
                for v in val:
                    ret.add(v)
        # Now convert the set of uniqe values to list to sort it for return. 
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
    # NOTE: with_group_labels=True is used so default behavior is to
    #  include group labels as YAML comments.  But tests can pass False
    #  to bypass this and just test items written correctly.
    def regroup_data_file(self, element, with_group_labels=True):
        grouped_items = self.get_grouped_items(element)               
        items = []
        if grouped_items is None:
            return ""
        group_keys = grouped_items.keys()
        group_keys.sort()
        for group_key in group_keys:
            # Mark each group in the regrouped file with a group name label
            if with_group_labels:
                label = self._format_group_label(element, group_key)
                items.append(label)
            # Append the list of items for this group
            items.extend(grouped_items[group_key])
        # Pass the Items, regrouped, to be written to data file
        self._rewrite(items)
        # For conveninence, testing/debugging pass the same output back to stdout
        return "\n".join([str(item) for item in items])
        
    def backup(self, bak_file=None):
        if not bak_file:
            bak_file = self.bak_file
        self._backup(bak_file)
  
    def setconf(self, conf, value):
        self._set_conf(conf, value)

    
    #########
    # CLI API
    
    # Command line users use only this call, indirectly, by passing command lines
    #  to orgm.py#__main__(). Arg 'a' is optparser.args. Short here for cleaner code   
    # CLI API
    # Command line users use only this call, indirectly, by passing command lines
    #  to orgm.py#__main__()     
    def run_cli(self, title, args):  
        # Validate (TODO) and load args
        action, title, area, project, tags, actions, priority, due_date, note, \
            use_regex_match, filename, \
            by_title, by_area, by_project, by_tags, by_actions, by_priority =\
            self._run_cli_load_args(args)        
        # For actions matching on an element value, figure out which one
        # NOTE: Just uses first one. DOES NOT validate only one passed in 
        match_elem, match_val = \
            self._run_cli_get_match(action, title, tags, actions, note)        
                
        # For actions modified by a group_by arg, figure out which one
        group_elem = \
            self._run_cli_get_group_elem(action, by_title, by_area, by_project, \
                by_tags, by_actions, by_priority)
        
        # Now turn cmd line action and arguments into Organizem API call
        if action == Action.ADD:
            item = Item(title, \
                area=area, project=project, tags=tags, \
                actions=actions, priority=priority, due_date=due_date, \
                note=note)
            self.add_item(item)
            
        elif action == Action.ADD_EMPTY:
            self.add_empty()
        
        elif action == Action.REMOVE:
            self.remove_items(match_elem, match_val, use_regex_match)            

        elif action == Action.FIND:
            items = self.find_items(match_elem, match_val, use_regex_match)            
            for item in items:              
                print str(item)
        
        elif action == Action.SHOW_GROUPED:
            grouped_items = self.get_grouped_items(group_elem)            
            group_keys = grouped_items.keys()
            group_keys.sort()
            for group_key in group_keys:
                label = self._format_group_label(group_elem, group_key)
                print label
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

        elif action == Action.SETCONF_DATA_FILE:
            self.setconf(Conf.DATA_FILE, filename)
            
        elif action == Action.SETCONF_BAK_FILE:
            self.setconf(Conf.BAK_FILE, filename)


    #########
    # Helpers
    #########
    
    #####
    # CLI

    # TODO add validation here
    # TODO validate that --set_conf* also have non-empty --filename
    def _run_cli_load_args(self, args):    
        # Must split() the two list element types, so the string becomes Py list
        # Trim single and double quotes from each element
        # Do this to avoid matching bugs depending on how elements were entered
        #  in data file or from CLI
        tags = args.tags.split(',')
        tags = [self._trim_quotes(t).strip() for t in tags]        
        actions = args.actions.split(',')
        actions = [self._trim_quotes(a).strip() for a in actions]
        # Trim single or double quotes from elements that have string values
        action = self._trim_quotes(args.action)
        title = self._trim_quotes(args.title)
        area = self._trim_quotes(args.area)
        project = self._trim_quotes(args.project)
        priority = self._trim_quotes(args.priority)
        due_date = self._trim_quotes(args.due_date)
        note = self._trim_quotes(args.note)
        filename = self._trim_quotes(args.filename)
        
        # Validation
        if action == Action.ADD and not title:
            raise OrganizemIllegalUsageException("'--add' action must include '--title' element and a value for title.")            
        if (action == Action.SETCONF_DATA_FILE or action == Action.SETCONF_BAK_FILE) \
            and not filename:
            raise OrganizemIllegalUsageException("'--setconf_*' actions must include '--filename' element and a value for filename.")

        return (action, title, area, project, tags, actions, priority, due_date, note, \
            args.regex, filename, \
            args.by_title, args.by_area, args.by_project, args.by_tags, \
            args.by_actions, args.by_priority) 
     
    def _trim_quotes(self, arg):
        if arg is None or len(arg) < 2:
            return arg
        # Count leading and trailing quotes and slice them all away. Hacky.
        j = 0
        k = len(arg)
        while j < k and (arg[j] == '"' or arg[j] == "'"):
            j += 1
        while k > 0 and (arg[k-1] == '"' or arg[k-1] == "'"):
            k -= 1
        return arg[j:k]
        
    def _format_group_label(self, elem, group_key):
        group_label = ('# %s: %s' % (elem, group_key))
        border = '# ' + ((len(group_label) - 2) * '-')
        label = '\n\n' + border + '\n' + group_label + '\n' + border              
        return label

    def _run_cli_get_match(self, action, title, tags, actions, note):
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
        return (match_elem, match_val)
      
    def _run_cli_get_group_elem(self, action, by_title, by_area, by_project, by_tags, by_actions, by_priority):
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
            elif by_priority:
                group_elem = Elem.PRIORITY
        return group_elem
    
    
    ###############################
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
        elem_vals = [item.get_elem_val(element) for item in items]
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
    
    
    ######################
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
