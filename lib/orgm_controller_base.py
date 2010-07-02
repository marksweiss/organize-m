
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
    
    @staticmethod
    get_group_actions():
        return [SHOW_GROUPED, SHOW_ELEMENTS, REBUILD_GROUPED]

class ActionArg_(object):
    REGEX = 'regex'
    FILENAME = 'filename'
    
    def __init__(self):
        for elem in Elem.get_data_elems():
            self.__setattr__('BY_' + elem.upper())  

    @staticmethod
    elem_from_action_arg(arg):
        if arg in ACTION_ARG_LIST:
            # Trim the 'by_' off the front and return the Elem.* const
            return arg[3:]
        return None

    @staticmethod
    action_arg_from_elem(elem):
        arg = 'by_' + elem
        if arg in ACTION_ARG_LIST:
            return arg
        return None
    
    @staticmethod
    get_group_by_action_args():
        return ACTION_ARG_LIST
# Hack because we want to dynamically generate the actual 'BY_TITLE', 'BY_*' const attributes from
#  elem list and we still want the same ActionArg.ENUM syntax to refer to these as used for Action.ENUM
#  and Elem.ENUM elsewhere in code.  So ActionArg needs an __init__(), so need to create a "singleton"
ActionArg = ActionArg_()

class OrgmBaseController(object):
    def run_cmd(self, title, args):
        pass
