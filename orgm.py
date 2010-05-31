#!/usr/bin/env python

import sys
from optparse import OptionParser

from lib.item import Elem
from lib.organizem import OrgmCliController, Action, ActionArg

__author__ = ("Mark S. Weiss <markswess AT yahoo DOT com>")
# __docformat__ = "en"
# __revision__ = "$Id: odict.py 129 2005-09-12 18:15:28Z teknico $"
__version__ = "0.8.4"
# __all__ = [""]


# TODO Move into real config? Make user-configurable?
data_file = 'orgm.dat'
bak_file = data_file + '_bak'


def main(argv):
    """
    Collect the command line arguments and pass them to Organizem.py for processing.
    Coupled to Organizem.py#run_cli() in that these dest variable names must
    match what it expects.
    """
    usage = """
    [-a | --add] - adds an item to the data file

* Must include --title, and can optionally include any of the additional Element arguments below
[-t | --title]  - item title 
[-A | --area]  - area of responsibility that includes the item
[-p | --project]  - project the item is part of
[-T | --tags]  - tags associated with the item
[-c | --actions]  - item actions that need to be taken
[-P | --priority]  - item priority
[-d | --due_date] - date first action associated with item is due 
[-n | --note] - additional freeform text associated with item

--add --title "my item title" --area "my area" --project "my project" --tags "tag 1, tag 2"  --actions "["do this now", "do this later"]" --priority "P1" --due_date "5-5-2010" --note "This is a short note. Long ones should be edited in the file"
--add  # reorganized for readability only
      --title "my item title" 
      --area "my area" 
      --project "my project" 
      --tags "tag 1, tag 2"  
      --actions "do this now, do this later" 
      --priority "P1"
      --due_date "5-5-2010" 
      --note "This is a short note. Long ones should be edited in the file"

      
[-e | --add_empty]  - appends an empty new Item to the bottom of the data file


[-r | --remove] - removes 0 or more Items from the data file
* Must supply *one* Element type and value. All matching Items will be removed.
* Can supply optional arg to match Items on a regex rather than literal match
[-x | --regex ]

--remove --title "my item title"
--remove --title "my item t*"    
--remove --tags "tag1, tag2"
--remove --tags "tag1"
--remove --actions "do this now, do this later"
--remove --actions "do this now"
--remove --note "This is a short note. Long ones should be edited in the file"

 
[-f | --find] - finds 0 or more Items and returns it/them to stdout
* Must supply *one* Element type and value. All matching Items will be returned.
* Can supply optional --regex arg to match Items on a regex rather than literal match
[-x | --regex ]

--find --title "my item title"
--find --tags "tag1, tag2"
--find --tags "tag1"
--find --actions "do this now, do this later"
--find --actions "do this now"
--find --note "This is a short note. Long ones should be edited in the file"
--find --regex --title "my item t*"


[-s | --show_grouped] - show Items grouped by an Element type, sent to stdout 
* Must supply one Element type
[-1 | --by_title]
[-2 | --by_area]
[-3 | --by_project]
[-4 | --by_tags]
[-5 | --by_actions]
[-6 | --by_priority]

--show_grouped --by_title
--show_grouped --by_area
--show_grouped --by_project
--show_grouped --by_tags
--show_grouped --by_actions
--show_grouped --by_priority

[-S | --show_elements] - show all values for Elements of a given type, sent to stdout
* Must supply one Element type

--show_elements --by_title
--show_elements --by_area
--show_elements --by_project
--show_elements --by_tags
--show_elements --by_actions
--show_elements --by_priority


[-R | --rebuild_grouped] - rebuild the data file grouped by an Element type 
* Must supply one Element type

--rebuild_grouped --by_area
--rebuild_grouped --by_project
--rebuild_grouped --by_tags
--rebuild_grouped --by_actions
--rebuild_grouped --by_priority

[-b | --backup] - backup all item data
* Can optionally supply name of file to backup to. If none supplied default is used.
[-F | --filename]

--backup --file_name "/MyPath/MyBackupOrgmFile.dat"

[-D | --setconf_data_file] - Store a configuration for location of data file. Persisted and will be reused across Organize-m sessions.
--setconf_data_file --file_name "/MyPath/MyOrgmFile.dat"
[-B | --setconf_backup_file] - Store a configuration for location of backup file. Persisted and will be reused across Organize-m sessions.
--setconf_backup_file --file_name "/MyPath/MyBackupOrgmFile.dat"
  """

    parser = OptionParser(usage=usage)
    
    # CLI Action. All map to storing in same dest variable, so only one can be
    #  validly passed on each call.  So, if user passes more than one, using the
    #  interface incorrectly, the last one processed will win.
    parser.add_option("-a", "--add", 
                      action="store_const", const=Action.ADD, dest="action",  
                      help="Add an Item. Can include any Element args.")                      
    parser.add_option("-e", "--add_empty", 
                      action="store_const", const=Action.ADD_EMPTY, dest="action",                        
                      help="Add an empty Item to the end of the data file")
    parser.add_option("-r", "--remove", 
                      action="store_const", const=Action.REMOVE, dest="action",  
                      help="Remove an Item. Can include --regex flag arg to match by regex. Must include one Element arg to match on.")
    parser.add_option("-f", "--find", 
                      action="store_const", const=Action.FIND, dest="action",  
                      help="Find an Item. Can include --regex flag arg to match by regex. Must include one Element arg to match on.")
    parser.add_option("-s", "--show_grouped", 
                      action="store_const", const=Action.SHOW_GROUPED, dest="action",  
                      help="Display all items grouped by distinct values for the Element type provided. e.g. - grouped by Title.")
    parser.add_option("-S", "--show_elements", 
                      action="store_const", const=Action.SHOW_ELEMENTS, dest="action",  
                      help="Display all element values for the Element type provided. e.g. - all Projects.")
    parser.add_option("-R", "--rebuild_grouped", 
                      action="store_const", const=Action.REBUILD_GROUPED, dest="action",  
                      help="Rebuild the data file grouped by distinct values for the Element type provided. e.g. - grouped by Title.")
    parser.add_option("-b", "--backup", 
                      action="store_const", const=Action.BACKUP, dest="action",  
                      help="Backup data file. Takes mandatory additonal argument --filename [My_Filename.txt]")
                      
    # Configuration
    # Users call these to set config options that persist across calls to Organizem 
    #  and across shell sessions.  These are managed in a config by the app, but
    #  the user interacts with them only from CLI.  Thought about making the config
    #  editable, but it seemed to add a third interface for the user with no benefit.
    # The cost is that these CLI commands have slightly different semantics -- they
    #  are not per-call, but rather they are persistent.  To denote this they are
    #  all preceded with --setconf_*.
    # TODO ADD TO DOCS
    parser.add_option("-D", "--setconf_data_file",
                      action="store_const", const=Action.SETCONF_DATA_FILE, dest="action",
                      help="Alternate location for Organize-m data file. Optional. Default data file is 'orgm.dat'.")
    parser.add_option("-B", "--setconf_backup_file",
                      action="store_const", const=Action.SETCONF_BAK_FILE, dest="action",
                      help="Location for Organize-m backup file. If set, each call to --backup uses this location, unless that call passes a --filename arg, in which case the value for --filename will be used. Optional. Default data file is 'orgm.dat_bak'.")
  
    # CLI Modifiers/Options (or for the APL-ers in the room, "adverbs")
    # These modify the action which is the first arg.  
    # They must be second, preceding any element arguments.
    # --regex applies to --find and --remove, for more flexible matching of Items
    # --filename applies only to --backup
    parser.add_option("-x", "--regex", 
                      action="store_true", dest=ActionArg.REGEX, default=False,  
                      help="Forces all matching for a --find or --remove operation to use regex matching on the pattern passed in.")
    parser.add_option("-F", "--filename", 
                      action="store", dest=ActionArg.FILENAME,
                      help="The file to be used in the action passed in.  e.g. - backup --filename \"file of stuff.txt\"")
    # Grouping Modifiers
    parser.add_option("-1", "--by_title", 
                      action="store_true", dest=ActionArg.BY_TITLE, default=False,  
                      help="Modifies --show_elements to show values for --title Element of all Items")
    parser.add_option("-2", "--by_area", 
                      action="store_true", dest=ActionArg.BY_AREA, default=False,  
                      help="Modifies --show_elements to show values for --area. Modifies --show_grouped and --rebuild_grouped to group by --area Element values")
    parser.add_option("-3", "--by_project", 
                      action="store_true", dest=ActionArg.BY_PROJECT, default=False,  
                      help="Modifies --show_elements to show values for --project. Modifies --show_grouped and --rebuild_grouped to group by --project Element values")
    parser.add_option("-4", "--by_tags", 
                      action="store_true", dest=ActionArg.BY_TAGS, default=False,  
                      help="Modifies --show_elements to show values for --tags. Modifies --show_grouped and --rebuild_grouped to group by --tags Element values")
    parser.add_option("-5", "--by_actions", 
                      action="store_true", dest=ActionArg.BY_ACTIONS, default=False,  
                      help="Modifies --show_elements to show values for --actions. Modifies --show_grouped and --rebuild_grouped to group by --actions Element values")
    parser.add_option("-6", "--by_priority", 
                      action="store_true", dest=ActionArg.BY_PRIORITY, default=False,  
                      help="Modifies --show_elements to show values for --priority. Modifies --show_grouped and --rebuild_grouped to group by --priority Element values")
    
    # Elements
    # The data to be --add(ed), or the data to match on for --find and --remove
    parser.add_option("-t", "--title", 
                      action="store", dest=Elem.TITLE, default="",
                      help="Title of the Item. Mandatory")
    parser.add_option("-A", "--area", 
                      action="store", dest=Elem.AREA, default="",
                      help="Area of Responsibility for the Item. Optional.")                      
    parser.add_option("-p", "--project", 
                      action="store", dest=Elem.PROJECT, default="",
                      help="Project for the Item. Optional.")
    parser.add_option("-T", "--tags", 
                      action="store", dest=Elem.TAGS, default="",
                      help="Tags for the Item. Enclose in quotes and each token will be a separate Tag. Optional.")
    parser.add_option("-c", "--actions", 
                      action="store", dest=Elem.ACTIONS, default="",
                      help="Actions for the Item. Enclose in quotes and each token will be a separate Action. Optional.")
    parser.add_option("-P", "--priority", 
                      action="store", dest=Elem.PRIORITY, default="",
                      help="Priority of the Item. Optional.")
    parser.add_option("-d", "--due_date", 
                      action="store", dest=Elem.DUE_DATE, default="",
                      help="Due date for first due Action for the Item. Optional.")
    parser.add_option("-n", "--note", 
                      action="store", dest=Elem.NOTE, default="",
                      help="Additional note for the Item. Optional.")
     
    (options, args) = parser.parse_args()

    # Check for config from command line for data file
    data_file = None
    if options.action == 'setconf_data_file':
        data_file = eval('options.' + ActionArg.FILENAME)
    
    orgm = OrgmCliController(data_file=data_file)
    orgm.run_cmd(options.title, options)

    
if __name__ == "__main__":  
    sys.exit(main(sys.argv[1:]))
