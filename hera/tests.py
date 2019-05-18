import unittest
from model import Model

class TestModel(unittest.TestCase):
    def setUp(self):
        '''Set up a simple model.'''
        self.test_model = Model('Test')

    def test_init(self):
        '''Test the __init__ method.'''
        self.assertEqual('Test', self.test_model._Model__description)

    # DESCRITPION --------------------------------------------------------------
    def test_set_description(self):
        '''Test the set_description method.'''
        self.test_model.set_description('Funny')

        self.assertEqual('Funny', self.test_model._Model__description)

    def test_get_description(self):
        '''Test the get_description method.'''
        self.assertEqual('Test', self.test_model.get_description())

    # ACTIONS ------------------------------------------------------------------
    def test_add_actions(self):
        '''Test the add_actions method.'''
        # Check adding of a single action
        actions = self.test_model._Model__actions
        intentions = self.test_model._Model__intentions
        mechanisms= self.test_model._Model__consequences

        self.test_model.add_actions('A1')

        self.assertListEqual(['A1'], actions)
        self.assertDictEqual({'A1': ['A1']}, intentions)

        # Check adding of multiple actions and handling of duplicate action
        # adding
        self.test_model.add_consequences('C1')
        self.test_model.add_intentions('A1', 'C1')

        self.test_model.add_actions('A1', 'A2')

        self.assertListEqual(['A1', 'A2'], actions)
        self.assertDictEqual(
                {'A1': ['A1', 'C1'],
                 'A2': ['A2']},
                intentions)

    def test_remove_actions(self):
        '''Test the remove_actions method.'''
        actions = self.test_model._Model__actions
        intentions = self.test_model._Model__intentions

        self.test_model.add_actions('A1', 'A2')
        self.test_model.remove_actions('A2')

        self.assertListEqual(['A1'], actions)
        self.assertDictEqual({'A1': ['A1']}, intentions)

    # BACKGROUND ---------------------------------------------------------------
    def test_add_background(self):
        '''Test the add_background method.'''
        background = self.test_model._Model__background

        # Test insertion of a single background variable
        self.test_model.add_background('B1')

        self.assertListEqual(['B1'], background)

        # Test insertion of multiple variables and handling of duplicates
        self.test_model.add_background('B1', 'B2')

        self.assertListEqual(['B1', 'B2'], background)

    def test_remove_background(self):
        '''Test the remove_background method.'''
        background = self.test_model._Model__background

        self.test_model.add_background('B1', 'B2')
        self.test_model.remove_background('B1')

        self.assertListEqual(['B2'], background)

    # CONSEQUENCES -------------------------------------------------------------
    def test_add_consequences(self):
        consequences = self.test_model._Model__consequences

        # Test insertion of a single consequence
        self.test_model.add_consequences('C1')
        self.assertListEqual(['C1'], consequences)

        # Test inserion of multiple consequences and handling of duplicates
        self.test_model.add_consequences('C1', 'C2')
        self.assertListEqual(['C1', 'C2'], consequences)

    def test_remove_consequences(self):
        '''Test the remove_consequences method.'''
        consequences = self.test_model._Model__consequences
        intentions = self.test_model._Model__intentions
        mechanisms = self.test_model._Model__consequences
        utilities = self.test_model._Model__utilities

        # Set up a model
        self.test_model.add_consequences('C1', 'C2')
        self.test_model.add_actions('A1')

        self.test_model.set_utility('C1', 42)
        self.test_model.add_intentions('A1', 'C1')

        # Check model before removal of C1
        self.assertListEqual(['C1', 'C2'], consequences)
        self.assertDictEqual({'C1': 42}, utilities)
        self.assertDictEqual({'A1': ['A1', 'C1']}, intentions)

        self.test_model.remove_consequences('C1')

        # Check model after removal of C1
        self.assertListEqual(['C2'], consequences)
        self.assertDictEqual({}, utilities)
        self.assertDictEqual({'A1': ['A1']}, intentions)

    # MECHANISMS ---------------------------------------------------------------
    def test_set_mechanism(self):
        pass

    def test_remove_mechanism(self):
        '''Test the remove_mechanism method.'''
        pass

    # UTILITITES ---------------------------------------------------------------
    def test_set_utility(self):
        self.test_model.add_consequences('C1', 'C2')
        self.test_model.set_utility('C1', 42)
        self.test_model.set_utility('C1', -42, False)

        utilities = self.test_model._Model__utilities

        # Check if set_utility changes only the desired values
        self.assertEqual(42, utilities['C1'])
        self.assertEqual(-42, utilities['Not(\'C1\')'])

    def test_remove_utility(self):
        self.test_model.add_consequences('C1')
        self.test_model.set_utility('C1', 42)
        self.test_model.remove_utility('C1')

        self.assertDictEqual({}, self.test_model._Model__utilities)

    # INTENSIONS ---------------------------------------------------------------
    def test_set_intension(self):
        pass

if __name__ == '__main__':
    unittest.main()
