from element import Elem


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
    
    GROUP_ACTIONS = [SHOW_GROUPED, SHOW_ELEMENTS, REBUILD_GROUPED]
    
    @staticmethod
    def get_group_actions():
        return Action.GROUP_ACTIONS

class ActionArg_(object):
    REGEX = 'regex'
    FILENAME = 'filename'

    PFX = 'BY_'    
    
    def __init__(self):
        # This line is the whole reason for all this clumsy scaffolding -- build the group by
        #  enums dynamically from Elem fields, so that if we add new Elements to Item
        #  there is nothing to keep in synch here
        for elem in Elem.get_data_elems():
            self.__setattr__(self.PFX + elem.upper(), self.PFX.lower() + elem.lower())  

    def elem_from_action_arg(self, arg):
        if self._has_arg(arg):
            # Trim the 'by_' off the front and return the Elem.* const
            return arg[len(self.PFX) : ]
        return None

    def action_arg_from_elem(self, elem):
        arg = self.PFX.lower() + elem
        if self._has_arg(arg):
            return arg
        return None
    
    def _has_arg(self, arg):
        return arg.upper() in self.__dict__
    
    def get_group_by_action_args(self):
        # Return all attributes that start with 'BY_'
        return self.__dict__.values()

# Hack because we want to dynamically generate the actual 'BY_TITLE', 'BY_*' const attributes from
#  elem list and we still want the same ActionArg.ENUM syntax to refer to these as used for Action.ENUM
#  and Elem.ENUM elsewhere in code.  So ActionArg needs an __init__(), so need to create a "singleton"
ActionArg = ActionArg_()


class OrgmBaseController(object):
    # The interface that specific controllers must implement
    def run_cmd(self, title, args):
        pass
