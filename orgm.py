import sys
from optparse import OptionParser

from organizem import Organizem

def main(argv):
    parser = OptionParser()
    
    # CLI Actions
    parser.add_option("-d", "--add", help="Add an Item. Can include any Element args.")
    parser.add_option("-e", "--add_empty", help="Add an empty Item to the end of the data file")
    parser.add_option("-v", "--remove", help="Remove an Item. Can include --regex flag arg to match by regex. Must include one Element arg to match on.")
    parser.add_option("-f", "--find", help="Find an Item. Can include --regex flag arg to match by regex. Must include one Element arg to match on.")
    parser.add_option("-g", "--show_grouped", help="Display all items grouped by distinct values for the Element type provided. e.g. - grouped by Title.")
    parser.add_option("-s", "--show_elements", help="Display all element values for the Element type provided. e.g. - all Projects.")
    parser.add_option("-b", "--rebuild_grouped", help="Rebuild the data file grouped by distinct values for the Element type provided. e.g. - grouped by Title.")
    parser.add_option("-k", "--backup", help="Backup data file. Takes mandatory additonal argument --filename [My_Filename.txt]")
        
    # CLI Modifiers (or for the APL-ers in the room, "adverbs")
    # These modify the action which is the first arg.  They must be second, preceding any element arguments.
    parser.add_option("-x", "--regex", help="Forces all matching for a --find or --remove operation to use regex matching on the pattern passed in.")
    parser.add_option("-m", "--filename", help="The file to be used in the action passed in.  e.g. - backup --filename 'file of stuff.txt'")
    
    # Elements
    parser.add_option("-l", "--title", 
                      action="store", dest="title", default="DEFAULT TITLE",
                      help="Title of the Item. Mandatory")
    parser.add_option("-r", "--area", 
                      action="store", dest="area", default="",
                      help="Area of Responsibility for the Item. Optional.")                      
    parser.add_option("-p", "--project", 
                      action="store", dest="project", default="",
                      help="Project for the Item. Optional.")
    parser.add_option("-t", "--tags", 
                      action="store", dest="tags", default=[],
                      help="Tags for the Item. Enclose in quotes and each token will be a separate Tag. Optional.")
    parser.add_option("-n", "--actions", 
                      action="store", dest="actions", default=[],
                      help="Actions for the Item. Enclose in quotes and each token will be a separate Action. Optional.")
    parser.add_option("-d", "--due_date", 
                      action="store", dest="due_date", default="",
                      help="Due date for first due Action for the Item. Optional.")
    parser.add_option("-n", "--note", 
                      action="store", dest="note", default="",
                      help="Additional note for the Item. Optional.")
      
    (options, args) = parser.parse_args()

    orgm = Organizem()
    orgm.run_shell_command(title, )

    
if __name__ == '__main__':  
    sys.exit(main(sys.argv[1:]))