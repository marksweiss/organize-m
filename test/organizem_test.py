import unittest

import sys
sys.path.insert(0, '..')
from lib.item import Item, Elem
from lib.organizem import Organizem, Conf
from lib.orgm_controller_base import ActionArg


TEST_DATA_FILE = "orgm_test.dat"
TEST_BAK_FILE = "orgm_test_bak.dat"
IS_UNIT_TESTING = True
Organizem(TEST_DATA_FILE, IS_UNIT_TESTING).setconf(Conf.BAK_FILE, TEST_BAK_FILE)
      

class OrganizemTestCase(unittest.TestCase):
    
    # Helpers
    def _init_test_data_file(self):
        with open(TEST_DATA_FILE, 'w') as f:
            item = Item("TEST_ITEM")            
            f.write(str(item))
            
    # Tests
    def test_init_item(self):
        title = "title"
        item = Item(title)
        self.assertTrue(item != None)
        self.assertTrue(isinstance(item, Item))
        self.assertTrue(item.title == title)

    def test_init_organizem(self):
        self._init_test_data_file()
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        self.assertTrue(orgm != None)
        self.assertTrue(isinstance(orgm, Organizem))
        self.assertTrue(orgm.data_file == TEST_DATA_FILE)

    def test_add_item__find_item_by_title(self):
        self._init_test_data_file()
        title = "title"        
        item = Item(title)        
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.TITLE, title))

    def test_add_item__find_rgx_item_by_title(self):
        self._init_test_data_file()
        title = "title"
        rgx_match = "titl*"
        item = Item(title)
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.TITLE, rgx_match, use_regex_match=True))

    def test_add_item__find_items_by_area(self):
        self._init_test_data_file()
        title = "title"
        area = "my area"
        item = Item(title, {Elem.AREA : area})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.AREA, area))

    def test_add_item__find_rgx_item_by_area(self):
        self._init_test_data_file()
        title = "title"
        area = "area"
        rgx_match = "are*"
        item = Item(title, {Elem.AREA : area})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.AREA, rgx_match, use_regex_match=True))

    def test_add_item__find_items_by_project(self):
        self._init_test_data_file()
        title = "title"
        project = "my project"
        item = Item(title, {Elem.PROJECT : project})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.PROJECT, project))

    def test_add_item__find_rgx_items_by_project(self):
        self._init_test_data_file()
        title = "title"
        project = "my project"
        rgx_match = "my proj*"
        item = Item(title, {Elem.PROJECT : project})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.PROJECT, rgx_match, use_regex_match=True))

    def test_add_item__find_items_by_tags(self):
        self._init_test_data_file()
        title = "title"
        # Test case of single-value passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        tag1 = 'tag 1'
        tags1 = [tag1]
        item1 = Item(title, {Elem.TAGS : tags1})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Elem.TAGS, tag1))
        # Test case of multi-value list passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        tag2 = 'tag 2'
        tags2 = [tag1, tag2]
        item2 = Item(title, {Elem.TAGS : tags2})
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Elem.TAGS, tag2))
        self.assertTrue(orgm.find_items(Elem.TAGS, tags2))

    def test_add_item__find_rgx_items_by_tags(self):
        self._init_test_data_file()
        title = "title"
        # Test case of single-value passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        tag1 = 'tag 1001'
        tag1_rgx = 'tag 100*'
        tags1 = [tag1]
        item1 = Item(title, {Elem.TAGS : tags1})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Elem.TAGS, tag1_rgx, use_regex_match=True))
        # Test case of multi-value list passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        tag2 = 'tag 1012'
        tag2_rgx = 'tag 101*'        
        tags2 = [tag1, tag2]
        item2 = Item(title, {Elem.TAGS : tags2})
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Elem.TAGS, tag2_rgx, use_regex_match=True))

    def test_add_item__find_items_by_actions(self):
        self._init_test_data_file()
        title = "title"
        action1 = 'action 100'
        action1_rgx = 'action 10*'
        actions1 = [action1]
        # TODO FIX ALL THESE Itme() ctor calls
        item1 = Item(title, {Elem.ACTIONS : actions1})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Elem.ACTIONS, action1_rgx, use_regex_match=True))
        action2 = 'action 200'
        actions2 = [action1, action2]
        item2 = Item(title, {Elem.ACTIONS : actions2})
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Elem.ACTIONS, action2))
        self.assertTrue(orgm.find_items(Elem.ACTIONS, actions2))

    def test_add_item__find_rgx_items_by_actions(self):
        self._init_test_data_file()
        title = "title"
        # Test case of single-value passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        action1 = 'action 1010'
        action1_rgx = 'action 101*'
        actions1 = [action1]
        item1 = Item(title, {Elem.ACTIONS : actions1})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Elem.ACTIONS, action1_rgx, use_regex_match=True))
        # Test case of multi-value list passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        action2 = 'action 1020'
        action2_rgx = 'action 102*'        
        actions2 = [action1, action2]
        item2 = Item(title, {Elem.ACTIONS : actions2})
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Elem.ACTIONS, action2_rgx, use_regex_match=True))

    def test_add_item__find_items_by_priority(self):
        self._init_test_data_file()
        title = "title"
        priority = "P1"
        item = Item(title, {Elem.PRIORITY : priority})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.PRIORITY, priority))

    def test_add_item__find_rgx_items_by_priority(self):
        self._init_test_data_file()
        title = "title"
        priority = "P1"
        rgx_match = "P*"
        item = Item(title, {Elem.PRIORITY : priority})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.PRIORITY, rgx_match, use_regex_match=True))

    def test_add_item__find_items_by_note(self):
        self._init_test_data_file()
        title = "title"
        note = """* Support for reporting on metadata
** all titles (alpha order, due date order)
  ** all projects (alpha order)
    ** all areas (alpha order)
      ** all tags (alpha order)
        ** all actions (grouped by item, item next due date order)
    http://www.snippy.com

    ljalj;
  a             dafs            asdfdsa           wkwjl;qq;q;"""
        item = Item(title, {Elem.NOTE : note})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.NOTE, note))

    def test_add_item__find_rgx_items_by_note(self):
        self._init_test_data_file()
        title = "title"
        note = """* Support for reporting on metadata
** all titles (alpha order, due date order)
  ** all projects (alpha order)
    ** all areas (alpha order)
      ** all tags (alpha order)
        ** all actions (grouped by item, item next due date order)
    http://www.snippy.com

    ljalj;
  a             dafs            asdfdsa           wkwjl;qq;q;"""
        note_rgx = "\* Support for reporting *"
        item = Item(title, {Elem.NOTE : note})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.NOTE, note_rgx, use_regex_match=True))

    def test_remove_items_rgx_by_title(self):
        self._init_test_data_file()
        title = "title"
        rgx_match = "titl*"
        item = Item(title)
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)
        self.assertTrue(orgm.find_items(Elem.TITLE, rgx_match, use_regex_match=True))
        # NOTE: Now remove the item and check that it's not there any more
        orgm.remove_items(Elem.TITLE, rgx_match, use_regex_match=True)
        self.assertFalse(orgm.find_items(Elem.TITLE, rgx_match, use_regex_match=True))

    def test_remove_items_rgx_by_area(self):
        self._init_test_data_file()
        title = "title"
        area = "area"
        rgx_match = "are*"
        item = Item(title, {Elem.AREA : area})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)
        self.assertTrue(orgm.find_items(Elem.AREA, rgx_match, use_regex_match=True))
        orgm.remove_items(Elem.AREA, rgx_match, use_regex_match=True)
        self.assertFalse(orgm.find_items(Elem.AREA, rgx_match, use_regex_match=True))

    def test_remove_items_by_project(self):
        self._init_test_data_file()
        title = "title"
        project = "project"
        item = Item(title, {Elem.PROJECT : project})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)
        self.assertTrue(orgm.find_items(Elem.PROJECT, project))
        orgm.remove_items(Elem.PROJECT, project)
        self.assertFalse(orgm.find_items(Elem.PROJECT, project))

    def test_remove_items_by_tags(self):
        self._init_test_data_file()
        title = "title"
        tag1 = 'tag 1'
        tags1 = [tag1]
        item1 = Item(title, {Elem.TAGS : tags1})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Elem.TAGS, tag1))
        orgm.remove_items(Elem.TAGS, tag1)
        self.assertFalse(orgm.find_items(Elem.TAGS, tag1))
        tag2 = 'tag 2'
        tags2 = [tag1, tag2]
        item2 = Item(title, {Elem.TAGS : tags2})
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Elem.TAGS, tag2))
        self.assertTrue(orgm.find_items(Elem.TAGS, tags2))
        orgm.remove_items(Elem.TAGS, tags2)        
        self.assertFalse(orgm.find_items(Elem.TAGS, tags2))

    def test_remove_items_rgx_by_actions(self):
        self._init_test_data_file()
        title = "title"
        action1 = 'action 110'
        rgx_match = "action 11*"
        actions1 = [action1]
        item1 = Item(title, {Elem.ACTIONS : actions1})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Elem.ACTIONS, action1))
        orgm.remove_items(Elem.ACTIONS, rgx_match, use_regex_match=True)
        self.assertFalse(orgm.find_items(Elem.ACTIONS, action1))
        action2 = 'action 101'
        rgx_match = "action 10*"
        actions2 = [action1, action2]
        item2 = Item(title, {Elem.ACTIONS : actions2})
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Elem.ACTIONS, action2))
        self.assertTrue(orgm.find_items(Elem.ACTIONS, actions2))
        orgm.remove_items(Elem.ACTIONS, rgx_match, use_regex_match=True)        
        self.assertFalse(orgm.find_items(Elem.ACTIONS, actions2))

    def test_remove_items_by_note(self):
        self._init_test_data_file()
        title = "title"
        note = """* Support for reporting on metadata
** all titles (alpha order, due date order)
  ** all projects (alpha order)
    ** all areas (alpha order)
      ** all tags (alpha order)
        ** all actions (grouped by item, item next due date order)
    http://www.snippy.com

    ljalj;
  a             dafs            asdfdsa           wkwjl;qq;q;"""
        item = Item(title, {Elem.NOTE : note})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.NOTE, note))
        orgm.remove_items(Elem.NOTE, note)        
        self.assertFalse(orgm.find_items(Elem.NOTE, note)) 

    def test_remove_items_rgx_by_note(self):
        self._init_test_data_file()
        title = "title"
        note = """* Support for reporting on metadata
** all titles (alpha order, due date order)
  ** all projects (alpha order)
    ** all areas (alpha order)
      ** all tags (alpha order)
        ** all actions (grouped by item, item next due date order)
    http://www.snippy.com

    ljalj;
  a             dafs            asdfdsa           wkwjl;qq;q;"""
        note_rgx = "\* Support for reporting *"
        item = Item(title, {Elem.NOTE : note})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Elem.NOTE, note_rgx, use_regex_match=True))
        orgm.remove_items(Elem.NOTE, note_rgx, use_regex_match=True)        
        self.assertFalse(orgm.find_items(Elem.NOTE, note_rgx))  

    def test_get_all_titles(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        item1 = Item(title1)
        item2 = Item(title2)
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2) 
        # Have to handle the fact that init of test dat file includes dummy item with "TEST_ITEM" title       
        self.assertTrue(orgm.get_elements(Elem.TITLE) == ['TEST_ITEM', 'title 1', 'title 2'])

    def test_get_all_projects(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        project1 = 'project 1'
        project2 = 'project 2'
        item1 = Item(title1, {Elem.PROJECT : project1})
        item2 = Item(title2, {Elem.PROJECT : project2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        expected = ["''", 'project 1', 'project 2']
        actual = orgm.get_elements(Elem.PROJECT)
        # Have to handle the fact that init of test dat file includes dummy item with empty name        
        self.assertTrue(expected == actual)

    def test_get_all_areas(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        area1 = 'area 1'
        area2 = 'area 2'
        item1 = Item(title1, {Elem.AREA : area1})
        item2 = Item(title2, {Elem.AREA : area2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        expected = ["''", 'area 1', 'area 2']
        actual = orgm.get_elements(Elem.AREA)        
        # Have to handle the fact that init of test dat file includes dummy item with empty name        
        self.assertTrue(expected == actual)

    def test_get_all_tags(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        tags1 = ['tag 1', 'tag 2']
        tags2 = ['tag 3', 'tag 4']
        item1 = Item(title1, {Elem.TAGS : tags1})
        item2 = Item(title2, {Elem.TAGS : tags2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        expected = ['tag 1', 'tag 2', 'tag 3', 'tag 4']
        actual = orgm.get_elements(Elem.TAGS)
        # Have to handle the fact that init of test dat file includes dummy item with empty name
        self.assertTrue(expected == actual)

    def test_get_all_actions(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        actions1 = ['action 1', 'action 2']
        actions2 = ['action 3', 'action 4']
        item1 = Item(title1, {Elem.ACTIONS : actions1})
        item2 = Item(title2, {Elem.ACTIONS : actions2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        expected = ['action 1', 'action 2', 'action 3', 'action 4']
        actual = orgm.get_elements(Elem.ACTIONS)        
        # Have to handle the fact that init of test dat file includes dummy item with empty name
        self.assertTrue(expected == actual)

    def test_get_grouped_items_project(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        project1 = 'project 1'
        project2 = 'project 2'
        item1 = Item(title1, {Elem.PROJECT : project1})
        item2 = Item(title2, {Elem.PROJECT : project2})
        item3 = Item(title3, {Elem.PROJECT : project1})
        item4 = Item(title4, {Elem.PROJECT : project2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)
        expected1 = repr([{'item' : [{'title': 'title 1'}, {'area': "''"}, {'project': 'project 1'}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, {'item' : [{'title': 'title 3'}, {'area': "''"}, {'project': 'project 1'}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}])
        expected2 = repr([{'item' : [{'title': 'title 2'}, {'area': "''"}, {'project': 'project 2'}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, {'item' : [{'title': 'title 4'}, {'area': "''"}, {'project': 'project 2'}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}])
        actual = orgm.get_grouped_items(Elem.PROJECT)
        actual1 = repr(actual[project1])
        actual2 = repr(actual[project2])        
        self.assertTrue(expected1 == actual1)
        self.assertTrue(expected2 == actual2)

    def test_get_grouped_items_area(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        area1 = 'area 1'
        area2 = 'area 2'
        item1 = Item(title1, {Elem.AREA : area1})
        item2 = Item(title2, {Elem.AREA : area2})
        item3 = Item(title3, {Elem.AREA : area1})
        item4 = Item(title4, {Elem.AREA : area2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)        
        expected1 = repr([{'item' : [{'title': 'title 1'}, {'area': 'area 1'}, {'project': "''"}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, {'item' : [{'title': 'title 3'}, {'area': 'area 1'}, {'project': "''"}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}])
        expected2 = repr([{'item' : [{'title': 'title 2'}, {'area': 'area 2'}, {'project': "''"}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, {'item' : [{'title': 'title 4'}, {'area': 'area 2'}, {'project': "''"}, {'tags': []}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}])
        actual = orgm.get_grouped_items(Elem.AREA)      
        actual1 = repr(actual[area1])
        actual2 = repr(actual[area2])           
        self.assertTrue(expected1 == actual1)
        self.assertTrue(expected2 == actual2)

    def test_get_grouped_items_tags(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        tag1 = 'tag 1'
        tag2 = 'tag 2'
        tag3 = 'tag 3'
        tag4 = 'tag 4'
        tags1 = [tag1, tag2]
        tags2 = [tag3, tag4]
        item1 = Item(title1, {Elem.TAGS : tags1})
        item2 = Item(title2, {Elem.TAGS : tags2})
        item3 = Item(title3, {Elem.TAGS : tags1})
        item4 = Item(title4, {Elem.TAGS : tags2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        expected1 = repr([{'item' : [{'title': 'title 1'}, {'area': "''"}, {'project': "''"}, {'tags': [tag1, tag2]}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, \
                     {'item' : [{'title': 'title 3'}, {'area': "''"}, {'project': "''"}, {'tags': [tag1, tag2]}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}])
        expected2 = repr([{'item' : [{'title': 'title 1'}, {'area': "''"}, {'project': "''"}, {'tags': [tag1, tag2]}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, \
                     {'item' : [{'title': 'title 3'}, {'area': "''"}, {'project': "''"}, {'tags': [tag1, tag2]}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}])
        expected3 = repr([{'item' : [{'title': 'title 2'}, {'area': "''"}, {'project': "''"}, {'tags': [tag3, tag4]}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, \
                     {'item' : [{'title': 'title 4'}, {'area': "''"}, {'project': "''"}, {'tags': [tag3, tag4]}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}])
        expected4 = repr([{'item' : [{'title': 'title 2'}, {'area': "''"}, {'project': "''"}, {'tags': [tag3, tag4]}, {'actions': []}, {'priority': "''"}, {'due_date': "''"}, {'note': ''}]}, \
                     {'item' : [{'title': 'title 4'}, {'area': "''"}, {'project': "''"}, {'tags': [tag3, tag4]}, {'actions': []},{'priority': "''"},  {'due_date': "''"}, {'note': ''}]}])

        actual = orgm.get_grouped_items(Elem.TAGS)
        actual1 = repr(actual[tag1])
        actual2 = repr(actual[tag2])
        actual3 = repr(actual[tag3])
        actual4 = repr(actual[tag4])

        self.assertTrue(expected1 == actual1)
        self.assertTrue(expected2 == actual2)
        self.assertTrue(expected3 == actual3)
        self.assertTrue(expected4 == actual4)

    def test_regroup_data_file_project(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        project1 = 'project 1'
        project2 = 'project 2'
        item1 = Item(title1, {Elem.PROJECT : project1})
        item2 = Item(title2, {Elem.PROJECT : project2})
        item3 = Item(title3, {Elem.PROJECT : project1})
        item4 = Item(title4, {Elem.PROJECT : project2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Elem.PROJECT)
        new_data_file_str = orgm.regroup_data_file(Elem.PROJECT, ActionArg.ASCENDING, with_group_labels=False)
        grouped_items_str = []
        for group_key in grouped_items.keys():          
            for item in grouped_items[group_key]:
                grouped_items_str.append(str(item))
        grouped_items_str = "\n".join(grouped_items_str)        
        self.assertTrue(grouped_items_str == new_data_file_str)

    def test_regroup_data_file_area(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        area1 = 'area 1'
        area2 = 'area 2'
        item1 = Item(title1, {Elem.AREA : area1})
        item2 = Item(title2, {Elem.AREA : area2})
        item3 = Item(title3, {Elem.AREA : area1})
        item4 = Item(title4, {Elem.AREA : area2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Elem.AREA)
        new_data_file_str = orgm.regroup_data_file(Elem.AREA, ActionArg.ASCENDING, with_group_labels=False)
        grouped_items_str = []
        for group_key in grouped_items.keys():          
            for item in grouped_items[group_key]:
                grouped_items_str.append(str(item))
        grouped_items_str = "\n".join(grouped_items_str)
        self.assertTrue(grouped_items_str == new_data_file_str)

    def test_regroup_data_file_area_sort_desc(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        area1 = 'area 1'
        area2 = 'area 2'
        item1 = Item(title1, {Elem.AREA : area1})
        item2 = Item(title2, {Elem.AREA : area2})
        item3 = Item(title3, {Elem.AREA : area1})
        item4 = Item(title4, {Elem.AREA : area2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Elem.AREA)
        new_data_file_str = orgm.regroup_data_file(Elem.AREA, ActionArg.DESCENDING, with_group_labels=False)
        grouped_items_str = []
        group_keys = grouped_items.keys()
        group_keys.reverse()
        for group_key in group_keys:          
            for item in grouped_items[group_key]:
                grouped_items_str.append(str(item))
        grouped_items_str = "\n".join(grouped_items_str)
        self.assertTrue(grouped_items_str == new_data_file_str)

    def test_regroup_data_file_tags(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        tag1 = 'tag 1'
        tag2 = 'tag 2'
        tag3 = 'tag 3'
        tag4 = 'tag 4'
        tags1 = [tag1, tag2]
        tags2 = [tag3, tag4]
        item1 = Item(title1, {Elem.TAGS : tags1})
        item2 = Item(title2, {Elem.TAGS : tags2})
        item3 = Item(title3, {Elem.TAGS : tags1})
        item4 = Item(title4, {Elem.TAGS : tags2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Elem.TAGS)
        new_data_file_str = orgm.regroup_data_file(Elem.TAGS, ActionArg.ASCENDING, with_group_labels=False)
        grouped_items_str = []
        for group_key in grouped_items.keys():          
            for item in grouped_items[group_key]:
                grouped_items_str.append(str(item))
        grouped_items_str = "\n".join(grouped_items_str)
        self.assertTrue(grouped_items_str == new_data_file_str)

    def test_regroup_data_file_tags_sort_desc(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        tag1 = 'tag 1'
        tag2 = 'tag 2'
        tag3 = 'tag 3'
        tag4 = 'tag 4'
        tags1 = [tag1, tag2]
        tags2 = [tag3, tag4]
        item1 = Item(title1, {Elem.TAGS : tags1})
        item2 = Item(title2, {Elem.TAGS : tags2})
        item3 = Item(title3, {Elem.TAGS : tags1})
        item4 = Item(title4, {Elem.TAGS : tags2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Elem.TAGS)
        new_data_file_str = orgm.regroup_data_file(Elem.TAGS, ActionArg.DESCENDING, with_group_labels=False)
        grouped_items_str = []
        group_keys = grouped_items.keys()
        group_keys.reverse()
        for group_key in group_keys:          
            for item in grouped_items[group_key]:
                grouped_items_str.append(str(item))
        grouped_items_str = "\n".join(grouped_items_str)
        self.assertTrue(grouped_items_str == new_data_file_str)
    
    def test_backup(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        tag1 = 'tag 1'
        tag2 = 'tag 2'
        tag3 = 'tag 3'
        tag4 = 'tag 4'
        tags1 = [tag1, tag2]
        tags2 = [tag3, tag4]
        item1 = Item(title1, {Elem.TAGS : tags1})
        item2 = Item(title2, {Elem.TAGS : tags2})
        item3 = Item(title3, {Elem.TAGS : tags1})
        item4 = Item(title4, {Elem.TAGS : tags2})
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)        

        bak_data_file = 'orgm_test.dat_bak'
        orgm.backup(bak_data_file)
        import filecmp
        filecmp.cmp(TEST_DATA_FILE, bak_data_file)

    # NOTE: This is a maual test, no assert().  User must look at TEST_DATA_FILE
    #  and confirm there is a new empty item
    def test_add_empty(self):
        self._init_test_data_file()
        orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
        orgm.add_empty()

    #def test_add_item__find_item_by_title__cli(self):
    #    self._init_test_data_file()
    #    orgm = Organizem(TEST_DATA_FILE, IS_UNIT_TESTING)
    #    title = 'my item title'
    #    cmd = ['-- add', '--title', title]
    #    orgm.run_shell_cmd(cmd)                
    #    self.assertTrue(orgm.find_items(Elem.TITLE, title))


if __name__ == '__main__':  
    unittest.main()