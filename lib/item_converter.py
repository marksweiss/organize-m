from element import Elem
from item import Item  #@UnusedImport, suppress Eclipse warning, used dynamically in convert_to_item() eval 


class OrganizemItemDataConversionException(Exception): pass
  

class BaseItemConverter(object):
    @staticmethod
    def convert_to_item(item):
        pass

class YamlItemConverter(BaseItemConverter):

    @staticmethod
    def convert_to_item(py_item):
        """Converts Item serialized to Python object form, dicts and lists, to YAML"""
    
        # The list of names of elements an Item must have for this version
        elem_names = Elem.get_optional_data_elems()
        # List of names of elements in the py_item
        py_elem_names = YamlItemConverter._get_py_item_elems(py_item)

        # Item must have title element, so check for that first
        title = YamlItemConverter._get_py_item_title(py_item, py_elem_names)
    
        # Handling dynamic list of kwargs to __init__(), so build string
        #  dynamically and make __init__() call an eval()
        init_call = []
        init_call.append("Item('%s', {" % title)
        # eval(x) where x is a multiline string literal fails on
        #  exception from scanning literal and finding an EOL in it
        # So, store the multiline string in this local List.  Put the
        #  note_vals[idx] into the string to be evaled.
        # And, yes, this is a pretty sweet hack
        note_vals = []                
        # Algo:
        #  - Iterate the list of expected elements, item_elems
        #  - Test for matching elem in py_item passed in (which was loaded from data)
        #  - If found, add to kwargs list with py_item value for Item.__init__()
        #  - If not found, add to kwargs list with None value for Item.__init__()
        for elem_name in elem_names:
            if elem_name in py_elem_names:
                idx = py_elem_names.index(elem_name)
                py_elems = py_item[Elem.ROOT]
                py_elem_val = py_elems[idx][elem_name]
                py_elem_val = Elem.elem_init(elem_name, py_elem_val).escaped_str()                
                if py_elem_val:
                    # Handle special case of multiline string value for Note elem
                    # See comment above where note_vals[] is declared
                    if Elem.get_elem_type(elem_name) == Elem.MULTILINE_TEXT_TYPE:
                        note_vals.append(py_elem_val)
                        val_idx = len(note_vals) - 1
                        init_call.append("'%s' : note_vals[%i], " % (elem_name, val_idx))
                    else:
                        init_call.append("'%s' : %s, " % (elem_name, py_elem_val))
                else:
                    init_call.append("'%s' : None, " % elem_name)
            else:
                init_call.append("'%s' : None, " % elem_name)
        init_call.append('})')
        init_call = ''.join(init_call)

        item = eval(init_call)
        return item

    @staticmethod
    def _get_py_item_elems(py_item):
        py_elems = py_item[Elem.ROOT]
        num_elems = len(py_elems)
        return [py_elems[j].keys()[0] for j in range(0, num_elems)]

    @staticmethod
    def _get_py_item_title(py_item, py_elem_names):      
        # Elements in the py_item
        py_elems = py_item[Elem.ROOT]                
        if Elem.TITLE not in py_elem_names:
            raise OrganizemItemDataConversionException("Attempted to load Item from data file without required 'title' element")
        idx = py_elem_names.index(Elem.TITLE)
        title = py_elems[idx][Elem.TITLE]
        if not title:
            raise OrganizemItemDataConversionException("Attempted to load Item from data file without value for required 'title' element")
        return title
