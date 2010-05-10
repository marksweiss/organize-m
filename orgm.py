import sys
from optparse import OptionParser

from item import Elem
from organizem import Organizem, Action, ActionArg


def main(argv):
    """
    Collect the command line arguments and pass them to Organizem.py for processing.
    Coupled to Organizem.py#run_cli() in that these dest variable names must
    match what it expects.
    """
    usage = """python orgm [ACTION] [OPTIONAL MODIFIERS] [ELEMENTS VALUES [...]] (For complete usage documentation: http://github.com/marksweiss/organize-m)"""
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
    parser.add_option("-v", "--remove", 
                      action="store_const", const=Action.REMOVE, dest="action",  
                      help="Remove an Item. Can include --regex flag arg to match by regex. Must include one Element arg to match on.")
    parser.add_option("-f", "--find", 
                      action="store_const", const=Action.FIND, dest="action",  
                      help="Find an Item. Can include --regex flag arg to match by regex. Must include one Element arg to match on.")
    parser.add_option("-g", "--show_grouped", 
                      action="store_const", const=Action.SHOW_GROUPED, dest="action",  
                      help="Display all items grouped by distinct values for the Element type provided. e.g. - grouped by Title.")
    parser.add_option("-l", "--show_elements", 
                      action="store_const", const=Action.SHOW_ELEMENTS, dest="action",  
                      help="Display all element values for the Element type provided. e.g. - all Projects.")
    parser.add_option("-d", "--rebuild_grouped", 
                      action="store_const", const=Action.REBUILD_GROUPED, dest="action",  
                      help="Rebuild the data file grouped by distinct values for the Element type provided. e.g. - grouped by Title.")
    parser.add_option("-b", "--backup", 
                      action="store_const", const=Action.BACKUP, dest="action",  
                      help="Backup data file. Takes mandatory additonal argument --filename [My_Filename.txt]")
        
    # CLI Modifiers/Options (or for the APL-ers in the room, "adverbs")
    # These modify the action which is the first arg.  
    # They must be second, preceding any element arguments.
    # --regex applies to --find and --remove, for more flexible matching of Items
    # --filename applies only to --backup
    parser.add_option("-x", "--regex", 
                      action="store_true", dest=ActionArg.REGEX, default=False,  
                      help="Forces all matching for a --find or --remove operation to use regex matching on the pattern passed in.")
    parser.add_option("-n", "--filename", 
                      action="store", dest=ActionArg.FILENAME,
                      help="The file to be used in the action passed in.  e.g. - backup --filename 'file of stuff.txt'")
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
    
    # Elements
    # The data to be --add(ed), or the data to match on for --find and --remove
    parser.add_option("-t", "--title", 
                      action="store", dest=Elem.TITLE, default="DEFAULT TITLE",
                      help="Title of the Item. Mandatory")
    parser.add_option("-r", "--area", 
                      action="store", dest=Elem.AREA, default="",
                      help="Area of Responsibility for the Item. Optional.")                      
    parser.add_option("-p", "--project", 
                      action="store", dest=Elem.PROJECT, default="",
                      help="Project for the Item. Optional.")
    parser.add_option("-s", "--tags", 
                      action="store", dest=Elem.TAGS, default="",
                      help="Tags for the Item. Enclose in quotes and each token will be a separate Tag. Optional.")
    parser.add_option("-c", "--actions", 
                      action="store", dest=Elem.ACTIONS, default="",
                      help="Actions for the Item. Enclose in quotes and each token will be a separate Action. Optional.")
    parser.add_option("-u", "--due_date", 
                      action="store", dest=Elem.DUE_DATE, default="",
                      help="Due date for first due Action for the Item. Optional.")
    parser.add_option("-o", "--note", 
                      action="store", dest=Elem.NOTE, default="",
                      help="Additional note for the Item. Optional.")
      
    (options, args) = parser.parse_args()

    orgm = Organizem()
    orgm.run_cli(options.title, options)

    
if __name__ == '__main__':  
    sys.exit(main(sys.argv[1:]))
