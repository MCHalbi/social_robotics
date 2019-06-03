import unittest
from model import Model

class TestModel(unittest.TestCase):
    def setUp(self):
        '''Set up a simple model.'''
        self.test_model = Model('Test')

        self.test_model._Model__actions = ['A1', 'A2', 'A3']
        self.test_model._Model__background = ['B1']
        self.test_model._Model__consequences = ['C1', 'C2', 'C3', 'C4']

        self.test_model._Model__mechanisms = {
                'C1': ['B1', 'A1'],
                'C2': ['A1'],
                'C3': ['B1', 'A2'],
                'C4': ['A2'],
                }

        self.test_model._Model__utilities = {
                'C1': 10,
                'C2': -4,
                'C3': 10,
                'C4': -4,
                'Not(\'C1\')': -10,
                'Not(\'C2\')': 4,
                'Not(\'C3\')': -10,
                'Not(\'C4\')': 4,
                }

        self.test_model._Model__intentions = {
                'A1': ['A1', 'C1'],
                'A2': ['A2', 'C3'],
                'A3': ['A3'],
                }

    # GENERAL ------------------------------------------------------------------
    def test_init(self):
        '''Test __init__ method.'''
        self.test_model = Model('Test')
        self.assertEqual('Test', self.test_model._Model__description)

    def test_repr(self):
        string = ('{\n'
                  + '    "actions": [\n'
                  + '        "A1",\n'
                  + '        "A2",\n'
                  + '        "A3"\n'
                  + '    ],\n'
                  + '    "background": [\n'
                  + '        "B1"\n'
                  + '    ],\n'
                  + '    "consequences": [\n'
                  + '        "C1",\n'
                  + '        "C2",\n'
                  + '        "C3",\n'
                  + '        "C4"\n'
                  + '    ],\n'
                  + '    "description": "Test",\n'
                  + '    "intentions": {\n'
                  + '        "A1": [\n'
                  + '            "A1",\n'
                  + '            "C1"\n'
                  + '        ],\n'
                  + '        "A2": [\n'
                  + '            "A2",\n'
                  + '            "C3"\n'
                  + '        ],\n'
                  + '        "A3": [\n'
                  + '            "A3"\n'
                  + '        ]\n'
                  + '    },\n'
                  + '    "mechanisms": {\n'
                  + '        "C1": "And(\'A1\', \'B1\')",\n'
                  + '        "C2": "\'A1\'",\n'
                  + '        "C3": "And(\'A2\', \'B1\')",\n'
                  + '        "C4": "\'A2\'"\n'
                  + '    },\n'
                  + '    "utilities": {\n'
                  + '        "C1": 10,\n'
                  + '        "C2": -4,\n'
                  + '        "C3": 10,\n'
                  + '        "C4": -4,\n'
                  + '        "Not(\'C1\')": -10,\n'
                  + '        "Not(\'C2\')": 4,\n'
                  + '        "Not(\'C3\')": -10,\n'
                  + '        "Not(\'C4\')": 4\n'
                  + '    }\n'
                  + '}')

        self.assertEqual(string, repr(self.test_model))

    def test_reset(self):
        '''Test reset method.'''
        self.test_model.reset()
        self.assertEqual('Test', self.test_model._Model__description)
        self.assertListEqual([], self.test_model._Model__actions)
        self.assertListEqual([], self.test_model._Model__consequences)
        self.assertListEqual([], self.test_model._Model__background)
        self.assertDictEqual({}, self.test_model._Model__mechanisms)
        self.assertDictEqual({}, self.test_model._Model__utilities)
        self.assertDictEqual({}, self.test_model._Model__intentions)

    def test_check(self):
        pass

    def test_export(self):
        pass

    # DESCRITPION --------------------------------------------------------------
    def test_set_description(self):
        '''Test set_description method.'''
        self.test_model.set_description('Hello World!')
        self.assertEqual('Hello World!', self.test_model._Model__description)

    # ACTIONS ------------------------------------------------------------------
    def test_add_actions(self):
        '''Test add_actions method.'''
        # Adding a single action
        self.test_model.add_actions('A4')
        self.assertListEqual(['A1', 'A2', 'A3', 'A4'],
                             self.test_model._Model__actions)
        self.assertDictEqual({'A1': ['A1', 'C1'], 'A2': ['A2', 'C3'],
                              'A3': ['A3'], 'A4': ['A4']},
                             self.test_model._Model__intentions)

        # Adding multiple actions + duplicate handling
        self.test_model.add_actions('A2', 'A5')
        self.assertListEqual(['A1', 'A2', 'A3', 'A4', 'A5'],
                             self.test_model._Model__actions)
        self.assertDictEqual({'A1': ['A1', 'C1'], 'A2': ['A2', 'C3'],
                              'A3': ['A3'], 'A4': ['A4'], 'A5': ['A5']},
                             self.test_model._Model__intentions)

        # Error raising
        self.assertRaises(TypeError, self.test_model.add_actions, 42)

    def test_remove_actions(self):
        '''Test remove_actions method.'''
        # Remove single action
        self.test_model.remove_actions('A1')
        self.assertListEqual(['A2', 'A3'], self.test_model._Model__actions)
        self.assertDictEqual({'C1': ['B1'], 'C2': [],
                              'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)
        self.assertDictEqual({'A2': ['A2', 'C3'], 'A3': ['A3']},
                             self.test_model._Model__intentions)

        # Remove multiple actions + duplicate handling
        self.test_model.remove_actions('A1', 'A3')
        self.assertListEqual(['A2'], self.test_model._Model__actions)
        self.assertDictEqual({'C1': ['B1'], 'C2': [],
                              'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)
        self.assertDictEqual({'A2': ['A2', 'C3']},
                             self.test_model._Model__intentions)

        # Error raising
        self.assertRaises(TypeError, self.test_model.remove_actions, 42)

    def test_rename_action(self):
        '''Test rename_action method.'''
        # Rename an action
        self.test_model.rename_action('A1', 'A4')
        self.assertListEqual(['A4', 'A2', 'A3'],
                             self.test_model._Model__actions)
        self.assertDictEqual({'C1': ['B1', 'A4'], 'C2': ['A4'],
                              'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)
        self.assertDictEqual({'A4': ['A4', 'C1'], 'A2': ['A2', 'C3'],
                              'A3': ['A3']},
                             self.test_model._Model__intentions)
        # Error raising
        self.assertRaises(TypeError, self.test_model.rename_action, 42, 'A1')
        self.assertRaises(TypeError, self.test_model.rename_action, 'A4', 42)
        self.assertRaises(TypeError, self.test_model.rename_action, 42, 42)
        self.assertRaises(ValueError, self.test_model.rename_action, 'A4', 'A2')
        self.assertRaises(KeyError, self.test_model.rename_action, 'A1', 'A5')

    # BACKGROUND ---------------------------------------------------------------
    def test_add_background(self):
        '''Test add_background method.'''
        # Adding a single background condition
        self.test_model.add_background('B2')
        self.assertListEqual(['B1', 'B2'], self.test_model._Model__background)

        #Adding multiple background conditions + duplicate handling
        self.test_model.add_background('B2', 'B3')
        self.assertListEqual(['B1', 'B2', 'B3'],
                             self.test_model._Model__background)

        #Error raising
        self.assertRaises(TypeError, self.test_model.add_background, 42)

    def test_remove_background(self):
        '''Test remove_background method.'''
        self.test_model.remove_background('B1')
        self.assertListEqual([], self.test_model._Model__background)
        self.assertDictEqual({'C1': ['A1'], 'C2': ['A1'],
                              'C3': ['A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)

        # Error raising
        self.assertRaises(TypeError, self.test_model.remove_background, 42)

    def test_rename_background(self):
        '''Test rename_background method.'''
        self.test_model.rename_background('B1', 'B2')
        self.assertListEqual(['B2'], self.test_model._Model__background)
        self.assertDictEqual({'C1': ['B2', 'A1'], 'C2': ['A1'],
                              'C3': ['B2', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)

        # Error raising
        self.assertRaises(TypeError, self.test_model.rename_background,
                          42, 'B1')
        self.assertRaises(TypeError, self.test_model.rename_background,
                          'B2', 42)
        self.assertRaises(TypeError, self.test_model.rename_background,
                          42, 42)
        self.assertRaises(ValueError, self.test_model.rename_background,
                          'B2', 'B2')
        self.assertRaises(KeyError, self.test_model.rename_background,
                          'B1', 'B2')

    # CONSEQUENCES -------------------------------------------------------------
    def test_add_consequences(self):
        '''Test add_consequences method.'''
        # Add a single consequence
        self.test_model.add_consequences('C5')
        self.assertListEqual(['C1', 'C2', 'C3', 'C4', 'C5'],
                             self.test_model._Model__consequences)
        self.assertDictEqual({'C1': ['B1', 'A1'], 'C2': ['A1'],
                              'C3': ['B1', 'A2'], 'C4': ['A2'], 'C5': []},
                        self.test_model._Model__mechanisms)

        # Add multiple consequences + duplicate handling
        self.test_model.add_consequences('C5', 'C6')
        self.assertListEqual(['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
                             self.test_model._Model__consequences)
        self.assertDictEqual({'C1': ['B1', 'A1'], 'C2': ['A1'],
                              'C3': ['B1', 'A2'], 'C4': ['A2'], 'C5': [],
                              'C6': []},
                        self.test_model._Model__mechanisms)

        # Error raising
        self.assertRaises(TypeError, self.test_model.add_consequences, 42)

    def test_remove_consequences(self):
        '''Test remove_consequences method.'''
        # Remove single consequence
        self.test_model.remove_consequences('C1')
        self.assertListEqual(['C2', 'C3', 'C4'],
                             self.test_model._Model__consequences)
        self.assertDictEqual({'C2': ['A1'], 'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)
        self.assertDictEqual({'C2': -4, 'C3': 10, 'C4': -4,
                              'Not(\'C2\')': 4, 'Not(\'C3\')': -10,
                              'Not(\'C4\')': 4},
                             self.test_model._Model__utilities)
        self.assertDictEqual({'A1': ['A1'], 'A2': ['A2', 'C3'], 'A3': ['A3']},
                             self.test_model._Model__intentions)

        # Remove multiple consequences + duplicate handling
        self.test_model.remove_consequences('C1', 'C2')
        self.assertListEqual(['C3', 'C4'], self.test_model._Model__consequences)
        self.assertDictEqual({'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)
        self.assertDictEqual({'C3': 10, 'C4': -4,
                              'Not(\'C3\')': -10, 'Not(\'C4\')': 4},
                             self.test_model._Model__utilities)
        self.assertDictEqual({'A1': ['A1'], 'A2': ['A2', 'C3'], 'A3': ['A3']},
                             self.test_model._Model__intentions)

        # Error raising
        self.assertRaises(TypeError, self.test_model.remove_consequences, 42)

    def test_rename_consequence(self):
        '''Test rename_consequence method.'''
        self.test_model.rename_consequence('C1', 'C5')
        self.assertListEqual(['C5', 'C2', 'C3', 'C4'],
                             self.test_model._Model__consequences)
        self.assertDictEqual({'C5': ['B1', 'A1'], 'C2': ['A1'],
                              'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)
        self.assertDictEqual({'C5': 10, 'C2': -4, 'C3': 10, 'C4': -4,
                              'Not(\'C5\')': -10, 'Not(\'C2\')': 4,
                              'Not(\'C3\')': -10, 'Not(\'C4\')': 4},
                             self.test_model._Model__utilities)
        self.assertDictEqual({'A1': ['A1', 'C5'], 'A2': ['A2', 'C3'],
                              'A3': ['A3']}, self.test_model._Model__intentions)

        # Error raising
        self.assertRaises(TypeError, self.test_model.rename_consequence,
                          42, 'C1')
        self.assertRaises(TypeError, self.test_model.rename_consequence,
                          'C5', 42)
        self.assertRaises(TypeError, self.test_model.rename_consequence,
                          42, 42)
        self.assertRaises(ValueError, self.test_model.rename_consequence,
                          'C5', 'C2')
        self.assertRaises(KeyError, self.test_model.rename_consequence,
                          'C1', 'C6')

    # MECHANISMS ---------------------------------------------------------------
    def test_add_mechanisms(self):
        '''Test add_mechanisms method.'''
        # Add single mechanism
        self.test_model.add_mechanisms('C2', 'A2')
        self.assertDictEqual({'C1': ['B1', 'A1'], 'C2': ['A1', 'A2'],
                              'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)

        # Add multiple mechanisms + duplicate handling
        self.test_model.add_mechanisms('C4', 'B1', 'A2', 'A1')
        self.assertDictEqual({'C1': ['B1', 'A1'], 'C2': ['A1', 'A2'],
                              'C3': ['B1', 'A2'], 'C4': ['A2', 'B1', 'A1']},
                             self.test_model._Model__mechanisms)

        # Error raising
        self.assertRaises(TypeError, self.test_model.add_mechanisms, 'C1', 42)
        self.assertRaises(TypeError, self.test_model.add_mechanisms, 42, 'C1')
        self.assertRaises(KeyError, self.test_model.add_mechanisms, 'C5', 'A1')

    def test_remove_mechanisms(self):
        '''Test remove_mechanism method.'''
        # Remove single mechanism
        self.test_model.remove_mechanisms('C1', 'B1')
        self.assertDictEqual({'C1': ['A1'], 'C2': ['A1'],
                              'C3': ['B1', 'A2'], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)

        # Remove multiple mechanisms + duplicate handling
        self.test_model.remove_mechanisms('C3', 'A2', 'B1')
        self.assertDictEqual({'C1': ['A1'], 'C2': ['A1'],
                              'C3': [], 'C4': ['A2']},
                             self.test_model._Model__mechanisms)

        # Error raising
        self.assertRaises(TypeError, self.test_model.add_mechanisms, 'C1', 42)
        self.assertRaises(TypeError, self.test_model.add_mechanisms, 42, 'A1')

    # UTILITITES ---------------------------------------------------------------
    def test_set_utility(self):
        '''Test set_utility method.'''
        # Set a simple utility
        self.test_model.set_utility('C1', 42)
        self.assertDictEqual({'C1': 42, 'C2': -4, 'C3': 10, 'C4': -4,
                              'Not(\'C1\')': -10, 'Not(\'C2\')': 4,
                              'Not(\'C3\')': -10, 'Not(\'C4\')': 4},
                             self.test_model._Model__utilities)

        # Set a Not utility
        self.test_model.set_utility('C1', 23, False)
        self.assertDictEqual({'C1': 42, 'C2': -4, 'C3': 10, 'C4': -4,
                              'Not(\'C1\')': 23, 'Not(\'C2\')': 4,
                              'Not(\'C3\')': -10, 'Not(\'C4\')': 4},
                             self.test_model._Model__utilities)

        # Error raising
        self.assertRaises(TypeError, self.test_model.set_utility, 'C1', '42')
        self.assertRaises(TypeError, self.test_model.set_utility, 23, 42)
        self.assertRaises(KeyError, self.test_model.set_utility, 'C5', 42)

    def test_remove_utility(self):
        '''Test remove_utility method.'''
        # Remove a simple utility
        self.test_model.remove_utility('C1')
        self.assertDictEqual({'C2': -4, 'C3': 10, 'C4': -4,
                              'Not(\'C1\')': -10, 'Not(\'C2\')': 4,
                              'Not(\'C3\')': -10, 'Not(\'C4\')': 4},
                             self.test_model._Model__utilities)

        # Remove a Not utility
        self.test_model.remove_utility('C1', False)
        self.assertDictEqual({'C2': -4, 'C3': 10, 'C4': -4, 'Not(\'C2\')': 4,
                              'Not(\'C3\')': -10, 'Not(\'C4\')': 4},
                             self.test_model._Model__utilities)

        # Error raising
        self.assertRaises(TypeError, self.test_model.remove_utility, 42)

    # INTENTIONS ---------------------------------------------------------------
    def test_add_intentions(self):
        '''Test add_intentions method.'''
        # Add a single intention
        self.test_model.add_intentions('A1', 'C2')
        self.assertDictEqual({'A1': ['A1', 'C1', 'C2'], 'A2': ['A2', 'C3'],
                              'A3': ['A3']},
                             self.test_model._Model__intentions)

        # Add multiple intentions + duplicate handling
        self.test_model.add_intentions('A2', 'C2', 'C3')
        self.assertDictEqual({'A1': ['A1', 'C1', 'C2'],
                              'A2': ['A2', 'C3', 'C2'], 'A3': ['A3']},
                             self.test_model._Model__intentions)

        # Error raising
        self.assertRaises(TypeError, self.test_model.add_intentions, 42, 'C2')
        self.assertRaises(TypeError, self.test_model.add_intentions, 'A1', 42)
        self.assertRaises(KeyError, self.test_model.add_intentions, 'A4', 'C1')
        self.assertRaises(KeyError, self.test_model.add_intentions, 'A1', 'C5')

    def test_remove_intentions(self):
        '''Test remove_intentions method.'''
        # Remove a single intention
        self.test_model.remove_intentions('A1', 'C1')
        self.assertDictEqual({'A1': ['A1'], 'A2': ['A2', 'C3'],
                              'A3': ['A3']},
                             self.test_model._Model__intentions)

        # Remove multiple intentions + duplicate handling
        self.test_model._Model__intentions['A1'] = ['A1', 'C1', 'C2']
        self.test_model.remove_intentions('A1', 'C1', 'C2', 'C3')
        self.assertDictEqual({'A1': ['A1'], 'A2': ['A2', 'C3'],
                              'A3': ['A3']},
                             self.test_model._Model__intentions)

        # Error raising
        self.assertRaises(TypeError, self.test_model.remove_intentions,
                          42, 'C2')
        self.assertRaises(TypeError, self.test_model.remove_intentions,
                          'A1', 42)

if __name__ == '__main__':
    unittest.main()
