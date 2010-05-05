import unittest

from item import Item
from organizem import Organizem


TEST_DATA_FILE = "orgm_test.dat"


# TDD all the way ... :-)  
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
        orgm = Organizem(TEST_DATA_FILE)
        self.assertTrue(orgm != None)
        self.assertTrue(isinstance(orgm, Organizem))
        self.assertTrue(orgm.data_file == TEST_DATA_FILE)

    def test_add_item__find_item_by_title(self):
        self._init_test_data_file()
        title = "title"
        item = Item(title)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Item.Element.TITLE, title))

    def test_add_item__find_items_by_area(self):
        self._init_test_data_file()
        title = "title"
        area = "my area"
        item = Item(title, area=area)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Item.Element.AREA, area))

    def test_add_item__find_items_by_project(self):
        self._init_test_data_file()
        title = "title"
        project = "my project"
        item = Item(title, project=project)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Item.Element.PROJECT, project))

    def test_add_item__find_items_by_tags(self):
        self._init_test_data_file()
        title = "title"
        # Test case of single-value passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        tag1 = 'tag 1'
        tags1 = [tag1]
        item1 = Item(title, tags=tags1)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Item.Element.TAGS, tag1))
        # Test case of multi-value list passed to find_items() for a 
        #  element that is stored in item as a list (tags)
        tag2 = 'tag 2'
        tags2 = [tag1, tag2]
        item2 = Item(title, tags=tags2)
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Item.Element.TAGS, tag2))
        self.assertTrue(orgm.find_items(Item.Element.TAGS, tags2))

    def test_add_item__find_items_by_actions(self):
        self._init_test_data_file()
        title = "title"
        action1 = 'action 1'
        actions1 = [action1]
        item1 = Item(title, actions=actions1)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        self.assertTrue(orgm.find_items(Item.Element.ACTIONS, action1))
        action2 = 'action 2'
        actions2 = [action1, action2]
        item2 = Item(title, actions=actions2)
        orgm.add_item(item2)
        self.assertTrue(orgm.find_items(Item.Element.ACTIONS, action2))
        self.assertTrue(orgm.find_items(Item.Element.ACTIONS, actions2))

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
        item = Item(title, note=note)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item)                
        self.assertTrue(orgm.find_items(Item.Element.NOTE, note))

    def test_get_all_titles(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        item1 = Item(title1)
        item2 = Item(title2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2) 
        # Have to handle the fact that init of test dat file includes dummy item with "TEST_ITEM" title       
        self.assertTrue(orgm.get_elements(Item.Element.TITLE) == ['TEST_ITEM', 'title 1', 'title 2'])

    def test_get_all_projects(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        project1 = 'project 1'
        project2 = 'project 2'
        item1 = Item(title1, project=project1)
        item2 = Item(title2, project=project2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)        
        # Have to handle the fact that init of test dat file includes dummy item with empty name        
        self.assertTrue(orgm.get_elements(Item.Element.PROJECT) == ['', 'project 1', 'project 2'])

    def test_get_all_areas(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        area1 = 'area 1'
        area2 = 'area 2'
        item1 = Item(title1, area=area1)
        item2 = Item(title2, area=area2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)        
        # Have to handle the fact that init of test dat file includes dummy item with empty name        
        self.assertTrue(orgm.get_elements(Item.Element.AREA) == ['', 'area 1', 'area 2'])

    def test_get_all_tags(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        tags1 = ['tag 1', 'tag 2']
        tags2 = ['tag 3', 'tag 4']
        item1 = Item(title1, tags=tags1)
        item2 = Item(title2, tags=tags2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)        
        # Have to handle the fact that init of test dat file includes dummy item with empty name
        self.assertTrue(orgm.get_elements(Item.Element.TAGS) == [[], ['tag 1', 'tag 2'], ['tag 3', 'tag 4']])

    def test_get_all_actions(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        actions1 = ['action 1', 'action 2']
        actions2 = ['action 3', 'action 4']
        item1 = Item(title1, actions=actions1)
        item2 = Item(title2, actions=actions2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)        
        # Have to handle the fact that init of test dat file includes dummy item with empty name
        self.assertTrue(orgm.get_elements(Item.Element.ACTIONS) == [[], ['action 1', 'action 2'], ['action 3', 'action 4']])

    def test_get_grouped_items_project(self):
        self._init_test_data_file()
        title1 = 'title 1'
        title2 = 'title 2'
        title3 = 'title 3'
        title4 = 'title 4'
        project1 = 'project 1'
        project2 = 'project 2'
        item1 = Item(title1, project=project1)
        item2 = Item(title2, project=project2)
        item3 = Item(title3, project=project1)
        item4 = Item(title4, project=project2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)        
        expected1 = [{'item' : [{'title': 'title 1'}, {'area': ''}, {'project': 'project 1'}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, {'item' : [{'title': 'title 3'}, {'area': ''}, {'project': 'project 1'}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]
        expected2 = [{'item' : [{'title': 'title 2'}, {'area': ''}, {'project': 'project 2'}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, {'item' : [{'title': 'title 4'}, {'area': ''}, {'project': 'project 2'}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]
        actual = orgm.get_grouped_items(Item.Element.PROJECT)
        actual1 = actual[project1]
        actual2 = actual[project2]
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
        item1 = Item(title1, area=area1)
        item2 = Item(title2, area=area2)
        item3 = Item(title3, area=area1)
        item4 = Item(title4, area=area2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)        
        expected1 = [{'item' : [{'title': 'title 1'}, {'area': 'area 1'}, {'project': ''}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, {'item' : [{'title': 'title 3'}, {'area': 'area 1'}, {'project': ''}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]
        expected2 = [{'item' : [{'title': 'title 2'}, {'area': 'area 2'}, {'project': ''}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, {'item' : [{'title': 'title 4'}, {'area': 'area 2'}, {'project': ''}, {'tags': []}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]
        actual = orgm.get_grouped_items(Item.Element.AREA)      
        actual1 = actual[area1]
        actual2 = actual[area2]
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
        item1 = Item(title1, tags=tags1)
        item2 = Item(title2, tags=tags2)
        item3 = Item(title3, tags=tags1)
        item4 = Item(title4, tags=tags2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)
        
        expected1 = [{'item' : [{'title': 'title 1'}, {'area': ''}, {'project': ''}, {'tags': [tag1, tag2]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, {'item' : [{'title': 'title 3'}, {'area': ''}, {'project': ''}, {'tags': [tag1, tag2]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]
        expected2 = [{'item' : [{'title': 'title 1'}, {'area': ''}, {'project': ''}, {'tags': [tag1, tag2]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, \
                     {'item' : [{'title': 'title 3'}, {'area': ''}, {'project': ''}, {'tags': [tag1, tag2]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]
        expected3 = [{'item' : [{'title': 'title 2'}, {'area': ''}, {'project': ''}, {'tags': [tag3, tag4]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, \
                     {'item' : [{'title': 'title 4'}, {'area': ''}, {'project': ''}, {'tags': [tag3, tag4]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]
        expected4 = [{'item' : [{'title': 'title 2'}, {'area': ''}, {'project': ''}, {'tags': [tag3, tag4]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}, \
                     {'item' : [{'title': 'title 4'}, {'area': ''}, {'project': ''}, {'tags': [tag3, tag4]}, {'actions': []}, {'due_date': ''}, {'note': ''}]}]

        actual = orgm.get_grouped_items(Item.Element.TAGS)
        actual1 = actual[tag1]
        actual2 = actual[tag2]
        actual3 = actual[tag3]
        actual4 = actual[tag4]
                
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
        item1 = Item(title1, project=project1)
        item2 = Item(title2, project=project2)
        item3 = Item(title3, project=project1)
        item4 = Item(title4, project=project2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Item.Element.PROJECT)
        new_data_file_str = orgm.regroup_data_file(Item.Element.PROJECT)
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
        item1 = Item(title1, area=area1)
        item2 = Item(title2, area=area2)
        item3 = Item(title3, area=area1)
        item4 = Item(title4, area=area2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Item.Element.AREA)
        new_data_file_str = orgm.regroup_data_file(Item.Element.AREA)
        grouped_items_str = []
        for group_key in grouped_items.keys():          
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
        item1 = Item(title1, tags=tags1)
        item2 = Item(title2, tags=tags2)
        item3 = Item(title3, tags=tags1)
        item4 = Item(title4, tags=tags2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)

        grouped_items = orgm.get_grouped_items(Item.Element.TAGS)
        new_data_file_str = orgm.regroup_data_file(Item.Element.TAGS)
        grouped_items_str = []
        for group_key in grouped_items.keys():          
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
        item1 = Item(title1, tags=tags1)
        item2 = Item(title2, tags=tags2)
        item3 = Item(title3, tags=tags1)
        item4 = Item(title4, tags=tags2)
        orgm = Organizem(TEST_DATA_FILE)
        orgm.add_item(item1)
        orgm.add_item(item2)
        orgm.add_item(item3)
        orgm.add_item(item4)        
        
        bak_data_file = 'orgm_test.dat_bak'
        orgm.backup(bak_data_file)
        import filecmp
        filecmp.cmp(TEST_DATA_FILE, bak_data_file)
        

if __name__ == '__main__':
    unittest.main()