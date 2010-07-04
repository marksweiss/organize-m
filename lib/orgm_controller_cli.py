from orgm_controller_base import OrgmBaseController, Action, ActionArg
from organizem import Organizem, Conf
from element import Elem
from item import Item


class OrganizemIllegalUsageException(Exception): pass


class OrgmCliController(OrgmBaseController):

    def __init__(self, data_file=None, is_unit_testing=False):
        self._orgm_api = Organizem(data_file, is_unit_testing)

    # Command line users use only this call, indirectly, by passing command lines
    #  to orgm.py#__main__().   
    # CLI API
    def run_cmd(self, title, args):        
        # Validate and load args
        action, args = self._format_and_validate(args)        
        # For actions matching on an element value, figure out which one
        # NOTE: Just uses first one. DOES NOT validate only one passed in 
        match_elem, match_val = self._get_match(action, args)        
            
        # For actions modified by a group_by arg, figure out which one
        group_elem = self._get_group(action, args)
    
        # Now turn cmd line action and arguments into Organizem API call
        if action == Action.ADD:            
            self._orgm_api.add_item(Item(args[Elem.TITLE], args))
        
        elif action == Action.ADD_EMPTY:
            self._orgm_api.add_empty()
    
        elif action == Action.REMOVE:
            self._orgm_api.remove_items(match_elem, match_val, args[ActionArg.REGEX])            

        elif action == Action.FIND:
            items = self._orgm_api.find_items(match_elem, match_val, args[ActionArg.REGEX])            
            for item in items:              
                print str(item)
    
        elif action == Action.SHOW_GROUPED:
            grouped_items = self._orgm_api.get_grouped_items(group_elem)            
            group_keys = grouped_items.keys()
            group_keys.sort()
            for group_key in group_keys:
                label = self._orgm_api.format_group_label(group_elem, group_key)
                print label
                for item in grouped_items[group_key]:                    
                    print str(item)
    
        elif action == Action.SHOW_ELEMENTS:
            elems = self._orgm_api.get_elements(group_elem)            
            elems.sort()
            for elem in elems:              
                print elem
                
        elif action == Action.REBUILD_GROUPED:
            self._orgm_api.regroup_data_file(group_elem)
        
        elif action == Action.BACKUP:
            self._orgm_api.backup(args[ActionArg.FILENAME])

        elif action == Action.SETCONF_DATA_FILE:
            self._orgm_api.setconf(Conf.DATA_FILE, args[ActionArg.FILENAME])
        
        elif action == Action.SETCONF_BAK_FILE:
            self._orgm_api.setconf(Conf.BAK_FILE, args[ActionArg.FILENAME])

    # Helpers
    def _format_and_validate(self, args):    
        # Unpack args, trim and clean, repack
        
        # Get action first for clarity of code here
        # TODO - expunge the magic string!
        action = OrgmCliController._trim_quotes(args['action'])                
        # Process all the data elements, values for fields in Elem, dynamically
        for elem in Elem.get_data_elems():
            elem_type = Elem.get_elem_type(elem)
            if elem_type == Elem.LIST_TYPE:
                # Must split() the two list element types, so the string becomes Py list
                # Trim single and double quotes from each element
                # NOTE: _trim_quotes() keeps args not passed as None and empty strings as empty, 
                #  which is *crucial* to logic of _run_cli_get_group_elem() below        
                args[elem] = [OrgmCliController._trim_quotes(t).strip() for t in args[elem].split(',')]        
            elif elem_type == Elem.TEXT_TYPE:
                args[elem] = OrgmCliController._trim_quotes(args[elem])
        # Process filename
        args[ActionArg.FILENAME] = OrgmCliController._trim_quotes(args[ActionArg.FILENAME])
    
        # Validation
        if action == Action.ADD and not args[Elem.TITLE]:
            raise OrganizemIllegalUsageException("'--add' action must include '--title' element and a value for title.")            
        elif (action == Action.SETCONF_DATA_FILE or action == Action.SETCONF_BAK_FILE) \
            and not args[ActionArg.FILENAME]:
            raise OrganizemIllegalUsageException("'--setconf_*' actions must include '--filename' element and a value for filename.")

        return (action, args)
         
    def _get_match(self, action, args):
        match_elem = None
        match_val = None
        if action == Action.FIND or action == Action.REMOVE:
            for elemkey in Elem.get_data_elems():
                if elemkey in args:
                    argval = args[elemkey]
                    if len(argval):
                        match_elem = elemkey
                        match_val = argval
                        break
            # Validate that we have match_elem and match_val if action requires them
            if match_elem is None or match_val is None:
                raise OrganizemIllegalUsageException("'--find and --remove must include an element (e.g. --title) and a value for that element.")                
        return (match_elem, match_val)
  
    def _get_group(self, action, args):        
        group_elem = None
        if Action.is_group_action(action):
            for action_arg_key in ActionArg.get_group_by_action_args():                
                if action_arg_key in args and args[action_arg_key]:
                    group_elem = ActionArg.elem_from_action_arg(action_arg_key)                
            # Validate that we have group_elem if action requires it
            if group_elem is None:
                raise OrganizemIllegalUsageException("'--show_elements, --show_grouped and --rebuild_grouped must include a grouping element (e.g. --by_title).")
        return group_elem
  
    @staticmethod
    def _trim_quotes(arg):
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
