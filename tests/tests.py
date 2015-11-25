import unittest

from weatherchecker import helpers

class HelperTests(unittest.TestCase):
    module = helpers
    def unit_db_find(self):
        spec_table = [
{'name': "Tom", 'age': 10},
{'name': "Mark", 'age': 5},
{'name': 'Pam', 'age': 10},
{'name': "Pam", 'age': 7},
{'name': "Mike", 'age': 7}
]

        func = self.module.db_find
        spec_args = {'table': spec_table, 'query': {'name': 'Pam', 'age': 7}}
        spec_result = [{'age': 7, 'name': 'Pam'}]

        result = func(**spec_args)
        return {'expectation': spec_result, 'result': result}

    def test_db_find(self):
        unit = self.unit_db_find()
        self.assertTrue(unit['expectation'] == unit['result'])

    def unit_db_remove(self):
        spec_table = [
{'name': "Tom", 'age': 10},
{'name': "Mark", 'age': 5},
{'name': 'Pam', 'age': 10},
{'name': "Pam", 'age': 7},
{'name': "Mike", 'age': 7}
]

        func = self.module.db_remove
        spec_args = {'table': spec_table, 'query': {'name': 'Pam', 'age': 7}}
        spec_result = [
{'name': "Tom", 'age': 10},
{'name': "Mark", 'age': 5},
{'name': 'Pam', 'age': 10},
{'name': "Mike", 'age': 7}
]

        func(**spec_args)
        return {'expectation': spec_result, 'result': spec_table}

    def test_db_remove(self):
        unit = self.unit_db_remove()
        self.assertTrue(unit['expectation'] == unit['result'])


if __name__ == "__main__":
    unittest.main()
