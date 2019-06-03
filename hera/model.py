# Authors: Lukas Halbritter <halbritl@informatik.uni-freiburg.de>,
#          Windy Phung <phungw@informatik.uni-freiburg.de>
# Copyright 2019
'''This module provides the functionality to build hera models.'''
import json
import os
from ethics.semantics import CausalModel

class Model:
    '''This class represents a Utility-based Causal Agency Models.'''
    def __init__(self, description):
        '''Initialize the model with a description.'''
        self.__description = description
        self.__actions = []
        self.__background = []
        self.__consequences = []
        self.__mechanisms = {}
        self.__utilities = {}
        self.__intentions = {}

    def __repr__(self):
        '''Return a json-formatted string which represents the model.'''
        mechanisms = {}
        for key, mech_list in self.__mechanisms.items():
            quoted_mechs = [self.__quote_str(mech) for mech in mech_list]
            quoted_mechs.sort()
            mechanisms[key] = self.__conjunct_list(quoted_mechs)

        model_dict = {
            'description': self.__description,

            'actions': self.__actions,
            'background': self.__background,
            'consequences': self.__consequences,

            'mechanisms': mechanisms,
            'utilities': self.__utilities,
            'intentions': self.__intentions,
            }

        return json.dumps(model_dict, indent=4, sort_keys=True)

    def reset(self):
        '''Reset the model.
        Clear all lists and dictionaries, only the description stays unchanged.
        '''
        for var in vars(self):
            attr = getattr(self, var)
            if isinstance(attr, list) or isinstance(attr, dict):
                attr.clear()

    def check(self):
        '''Checks if all consequences can be reached (mechanism exists).'''
        for consequence in self.__consequences:
            if self.__mechanisms[consequence] == []:
                raise RuntimeError('Consequence {} cannot be reached since '
                                   .format(consequence)
                                   + 'there is no mechanism for it.')

    def export(self, assignment):
        '''Export the model as a CausalModel from the ethics module.

        Arguments:
        assignment -- A dictionary that assigns each action and background
                      condition a truth value
        '''
        # Check, if the assignment is valid
        if set(assignment.keys()) < set(self.__actions + self.__background):
            raise KeyError('The following variables have no assignment: {}'
                           .format(set(self.__actions + self.__background) -
                                   set(assignment.keys())))

        if set(assignment.keys()) != set(self.__actions + self.__background):
            raise KeyError('The assignment contains variables which are not in '
                           + 'the model: {}'
                           .format(set(assignment.keys()) -
                                   set(self.__actions + self.__background)))

        if set(assignment.values()) != {0, 1}:
            raise ValueError('Assignments must assign either 0 or 1 to a '
                             + 'variable. {} are no valid assignment values.'
                             .format(set(assignment.values()) - {0, 1}))

        filename = 'tmp_model.json'

        # Export model to temporary json file
        with open(filename, 'w') as tmp_file:
            tmp_file.write(repr(self))

        # Initialize a CausalModel with the json file
        hera_model = CausalModel(filename, assignment)

        # Remove the temporary file
        os.remove(filename)

        return hera_model

    # DESCRIPTION --------------------------------------------------------------
    def set_description(self, description):
        '''Set the description of the model.

        Arguments:
        description -- A string that describes the model.
        '''
        self.__verify_description(description)

        self.__description = description

    # ACTIONS ------------------------------------------------------------------
    def add_actions(self, *actions):
        '''Add one or more actions to the model.
        If the action is already in the list, it will not be added twice.

        Arguments:
        *actions -- One or multiple strings that represent action names.
        '''
        for action in actions:
            self.__verify_action(action)

            if action not in self.__actions:
                # Add the action to the list
                self.__actions.append(action)

                # Instantiate the intentions of the action with the action
                # itself
                self.__intentions[action] = [action]

    def remove_actions(self, *actions):
        '''Remove one or more actions from list of actions.
        If there is no such action in the list, this will be ignored.
        This also removes the intentions of this action and removes it from all
        mechanisms to keep the model consistent.

        Arguments:
        *actions -- One or multiple strings that represent action names.
        '''
        for action in actions:
            # Typecheck the action
            self.__verify_action(action)

            # If the action exists, remove it from the model.
            if action in self.__actions:
                self.__actions.remove(action)

                # Remove the intentions of the action from the model.
                del self.__intentions[action]

                # Remove the action from all mechanisms (if it occurs)
                self.__remove_item_from_list_dict(action, self.__mechanisms)

    def rename_action(self, action_old, action_new):
        '''Renames action and changes the action name accordingly in
        mechanism and intentions containing that action.

        Arguments:
        action_old -- Old action name.
        action_new -- New action name.
        '''
        # Check, if there is an action with the old name in the model and
        # typecheck the new name.
        self.__verify_action(action_old, True)
        self.__verify_action(action_new)

        self.__rename_item_in_list(action_old, action_new, self.__actions)

        # Rename action within mechanisms
        self.__rename_item_in_list_dict(action_old, action_new,
                                        self.__mechanisms)

        # Rename action within intentions
        self.__rename_item_in_list_dict(action_old, action_new,
                                        self.__intentions, True)

    # BACKGROUND ---------------------------------------------------------------
    def add_background(self, *background):
        '''Add one or more background conditions to the model.
        If the background condition is already in the list, it will not be added
        twice.

        Arguments:
        *background -- One or multiple strings that represent background
                       conditions.
        '''
        for bg_condition in background:
            # Assure that the condition is a string
            self.__verify_background(bg_condition)

            # Add the background condition to the background list
            self.__append_if_new(bg_condition, self.__background)

    def remove_background(self, *background):
        '''Remove one or more background conditions from the model.
        If there is no such background condition in the model, this will be
        ignored.

        Arguments:
        *background -- One or multiple strings that represent background
                       conditions.
        '''
        for bg_condition in background:
            # Typecheck the background consition
            self.__verify_background(bg_condition)

            # If the condition exists, remove it from the model.
            if bg_condition in self.__background:
                self.__background.remove(bg_condition)

                # Update mechanisms which contain the background
                self.__remove_item_from_list_dict(bg_condition,
                                                  self.__mechanisms)

    def rename_background(self, bg_old, bg_new):
        '''Renames background and changes the background name accordingly in
        mechanism containing that background.

        Arguments:
        bg_old -- Old name of the background condition
        bg_new -- New name of the background condition
        '''
        # Check, if there is a background condition with the old name in the
        # model and typecheck the new name.
        self.__verify_background(bg_old, check_if_in_model=True)
        self.__verify_background(bg_new)

        self.__rename_item_in_list(bg_old, bg_new, self.__background)

        # Rename background within mechanisms
        self.__rename_item_in_list_dict(bg_old, bg_new, self.__mechanisms)

    # CONSEQUENCES -------------------------------------------------------------
    def add_consequences(self, *consequences):
        '''Add one or more consequences to the model.
        If the consequence is already in the list, it will not be added twice.

        Arguments:
        *consequences -- One or multiple strings that represent consequences.
        '''
        for consequence in consequences:
            # Assure that the consequence is a string
            self.__verify_consequence(consequence)

            # If it does not already exists, add the consequence to the list
            self.__append_if_new(consequence, self.__consequences)

            self.__mechanisms[consequence] = []

    def remove_consequences(self, *consequences):
        '''Remove one or multiple consequences from the model.
        This also removes the mechanisms and utilites of the consequences.
        Intentions which contain the consequences are updated as well.

        Arguments:
        *consequences -- One or more strings which represent the consequence
                         names.
        '''
        for consequence in consequences:
            # Typecheck consequence
            self.__verify_consequence(consequence)

            # If the consequence exists, remove it from the model.
            if consequence in self.__consequences:
                self.__consequences.remove(consequence)

                # If consequence is part of a mechanism, delete mechanism.
                if consequence in self.__mechanisms:
                    del self.__mechanisms[consequence]

                # Remove the utilities of the consequence from the model
                for cons_string in [consequence, self.__not_str(consequence)]:
                    if cons_string in self.__utilities:
                        del self.__utilities[cons_string]

                # Remove the consequence from all intentions
                self.__remove_item_from_list_dict(consequence,
                                                  self.__intentions)

    def rename_consequence(self, con_old, con_new):
        '''Renames consequence and changes the consequence name accordingly in
        mechanisms, utilities and intentions containing that consequence.

        Arguments:
        con_old -- Old consequence name.
        con_new -- New consequence name.
        '''
        # Check, if there is a consequence with the old name in the model and
        # typecheck the new name.
        self.__verify_consequence(con_old, True)
        self.__verify_consequence(con_new)

        self.__rename_item_in_list(con_old, con_new, self.__consequences)

        # Rename consequence within mechanisms
        self.__rename_item_in_list_dict(con_old, con_new, self.__mechanisms,
                                        True)

        # Rename consequence within utilities
        self.__rename_key(con_old, con_new, self.__utilities)
        self.__rename_key(self.__not_str(con_old), self.__not_str(con_new),
                          self.__utilities)

        # Rename consequence within intentions
        self.__rename_item_in_list_dict(con_old, con_new, self.__intentions)

    # MECHANISMS ---------------------------------------------------------------
    def add_mechanisms(self, consequence, *variables):
        '''Add one or more variables to the mechanism of a consequence.
        If the variable is already in the list, it will not be added twice.

        Arguments:
        consequence -- The consequence for which the mechanism should be added.
        *mechanisms -- One or multiple strings that represent a mechanism.
        '''
        self.__verify_consequence(consequence, True)

        for variable in variables:
            # Assure that the variable is valid (exist in the model)
            self.__verify_variable(variable, True)

            # If it does not already exists, add the variable to the list
            self.__append_if_new(variable, self.__mechanisms[consequence])

    def remove_mechanisms(self, consequence, *mechanism):
        '''Remove one or more intended variables of the mechanism of a
        consequence.

        Arguments:
        consequence -- The consequence for which (parts of) the mechanism
        should be removed.
        *mechanism -- The (part of the) mechanism to be removed.
        '''
        self.__verify_consequence(consequence, True)

        for variable in mechanism:
            if variable in self.__mechanisms[consequence]:
                # TODO: del self.__mechanisms[consequence] ?
                self.__mechanisms[consequence].remove(variable)

    # UTLILITIES ---------------------------------------------------------------
    def set_utility(self, consequence, value, affirmation=True):
        '''Set the utility of an consequence.

        Arguments:
        consequence -- The consequence name of which the utility is set.
        value -- The value of the utility.
        affirmation -- True, if the utility of the consequence itself is set.
                       False, if the utlility of not reaching the consequence is
                       to be set.
        '''
        # Assure that the consequence is in the model and typechek the value of
        # the utility and the consequence
        self.__verify_utility(value)
        self.__verify_consequence(consequence, True)

        # Adjust the consequence name if the utility of not reaching the
        # consequence is to be set
        if not affirmation:
            consequence = self.__not_str(consequence)

        self.__utilities[consequence] = value

    def remove_utility(self, consequence, affirmation=True):
        '''Remove the utility of a consequence.
        If there is no such consequence, the method does nothing.

        Arguments:
        consequence -- The consequence of which the utility is to be removed
        affirmation -- True, if the utility of the consequence itself is to be
                           removed.
                       False, if the utlility of not reaching the consequence is
                           to be removed.
        '''
        # Typecheck consequence
        self.__verify_consequence(consequence)

        if not affirmation:
            consequence = self.__not_str(consequence)

        # Remove the utility of the consequence, if it exists
        if consequence in self.__utilities:
            del self.__utilities[consequence]

    # INTENTIONS ---------------------------------------------------------------
    def add_intentions(self, action, *consequences):
        '''Add one or more consequences to the intention of an action.
        If the consequence is already in the list, it will not be added twice.

        Arguments:
        *consequences -- One or multiple strings that represent consequences
        '''
        self.__verify_action(action, True)

        for consequence in consequences:
            self.__verify_consequence(consequence, True)

            # If the consequence is not already in the intention of the action,
            # add it
            self.__append_if_new(consequence, self.__intentions[action])

    def remove_intentions(self, action, *consequences):
        '''Remove one or more consequences of an action.
        It is not possible, to remove the action itself from the intentions of
        an action.

        Arguments:
        action -- The action for which the intentions should be removed
        *consequences -- The consequences to be removed
        '''
        self.__verify_action(action, True)

        for consequence in consequences:
            self.__verify_consequence(consequence, True)

            if consequence in self.__intentions[action]:
                self.__intentions[action].remove(consequence)

    # VERIFICATION METHODS -----------------------------------------------------
    def __verify_description(self, description):
        '''Verify a description.
        Raise an error, if the description is not valid.
        '''
        # Assure that the description is a string
        self.__check_type(description, str,
                          'Model description must be a string.')

    def __verify_action(self, action, check_if_in_model=False):
        '''Verify an action.
        Raise an error, if the action is not valid.

        Arguments:
        check_if_in_model -- True, if the method should check whether the action
                             name is registered in the models list of actions.
        '''
        # Assure that the action is a string
        self.__check_type(action, str, 'An action name must be a string.')

        # Assure that the action is actually an action of the model
        if check_if_in_model:
            self.__check_if_in_model(action, self.__actions, 'action')

    def __verify_background(self, bg_condition, check_if_in_model=False):
        '''Verify a background condition.
        Raise an error, if the condition is not valid.

        Arguments:
        check_if_in_model -- True, if the method should check whether the
                             background condition name is registered in the
                             models background list.
        '''
        # Assure that the condition is a string
        self.__check_type(bg_condition, str,
                          'A background condition name must be a string.')

        # Assure that the condition is actually in the background of the model
        if check_if_in_model:
            self.__check_if_in_model(bg_condition, self.__background,
                                     'background condition')

    def __verify_consequence(self, consequence, check_if_in_model=False):
        '''Verify a consequence.
        Raise an error, if the consequence is not valid.

        Arguments:
        check_if_in_model -- True, if the method should check whether the
                             consequence name is registered in the models list
                             of consequences.
        '''
        # Assure that the name of the consequence is a string
        self.__check_type(consequence, str,
                          'An consequence name must be a string.')

        # Assure that the consequence is actually a consequence of the model
        if check_if_in_model:
            self.__check_if_in_model(consequence, self.__consequences,
                                     'consequence')

    def __verify_utility(self, utility):
        '''Verify a utility.
        Raise an error, if the utility is not valid.
        '''
        # Assure that the name of the consequence is a string
        self.__check_type(utility, int,
                          'A utility name must be an integer value.')

    def __verify_variable(self, variable, check_if_in_model=False):
        '''Verify a variable. This may be the name of an action, background
        condition or a consequence.
        Raise an error, if the consequence is not valid.

        Arguments:
        check_if_in_model -- True, if the method should check whether the
                             variable is a variable of the model.
        '''
        # Assure that the name of the consequence is a string
        self.__check_type(variable, str, 'A variable name must be a string.')

        # Assure that the consequence is actually a consequence of the model
        if check_if_in_model:
            all_vars = self.__actions + self.__consequences + self.__background
            self.__check_if_in_model(variable, all_vars, 'variable')

    @staticmethod
    def __check_type(obj, obj_type, error_msg):
        '''A generic way for raising type errors.
        This method raises a TypeError, if a given object does not match a given
        type.

        Arguments:
        obj -- The object in question
        obj_type -- The desired type of the object
        error_msq -- The error message that will be shown when a TypeError is
                     raised
        '''
        if not isinstance(obj, obj_type):
            raise TypeError(error_msg)

    @staticmethod
    def __check_if_in_model(obj, obj_list, obj_name):
        '''Raise a KeyError, if a given object is not in a given list.

        Argumens:
        obj -- The object in question
        obj_list -- The list in which the object should be
        obj_name -- The name of the object (used to generate the error message
                    printed by the KeyError)
        '''
        if obj not in obj_list:
            raise KeyError('{} is no {} of the model.'.format(obj, obj_name))

    # STRING MODIFIERS ---------------------------------------------------------
    @staticmethod
    def __not_str(variable):
        '''Reuturn a string of the form
            Not('v')
        for a given variable v.

        Arguments:
        variable -- A variable string
        '''
        return 'Not(\'' + variable + '\')'

    @staticmethod
    def __quote_str(variable):
        '''Reuturn a string of the form
            'v'
        for a given variable v.

        Arguments:
        variable -- A variable string
        '''
        return '\'' + variable + '\''

    @staticmethod
    def __conjunct_list(str_list):
        '''Create a conjunction string of the form
            And( ... And(And(l1, l2), l3) ..., ln)
        from a list of string literals.

        Arguments:
        str_list -- A list of strings literals
        '''
        if not str_list:
            return ''

        curr = str_list.pop(0)
        for string in str_list:
            curr = 'And(' + curr + ', ' + string + ')'

        return curr

    # LIST AND DICTIONARY MODIFIERS --------------------------------------------
    @staticmethod
    def __remove_item_from_list_dict(item, list_dict):
        '''Remove an item from all lists in a dictionary of lists.

        Arguments:
        item -- A item that's to be removed from all lists in the dictionary
        list_dict -- A dictionary of lists
        '''
        for variable, item_list in list_dict.items():
            if item in item_list:
                list_dict[variable].remove(item)

    def __rename_item_in_list_dict(self, item_old, item_new, list_dict,
                                   rename_keys=False):
        '''Replace all occurences of an item in all lists in a dictionary of
        lists.

        Arguments:
        item_old -- The item that's to be replaced
        item_new -- The item that replaces the old item
        list_dict -- A dictionary of lists
        rename_keys -- If True, the replacement also affects the dict keys.
        '''
        # Rename the dict keys
        if rename_keys:
            self.__rename_key(item_old, item_new, list_dict)

        # Replace all occurences of the old item with the new item
        for item_list in list_dict.items():
            for pos, item in enumerate(item_list):
                if item == item_old:
                    item_list[pos] = item_new

    @staticmethod
    def __rename_item_in_list(item_old, item_new, item_list):
        '''Replace an item in a list with another item.
        This assumes that the item occurs exactly once in the list.

        Arguments:
        item_old -- The old item
        item_new -- The new item
        item_list -- The list where the item should be replaced
        '''
        pos = item_list.index(item_old)
        item_list[pos] = item_new

    @staticmethod
    def __append_if_new(item, item_list):
        '''Append an item to a list, if this item is not already present in the
        list.

        Arguments:
        item -- An item
        item_list -- A list
        '''
        if item not in item_list:
            item_list.append(item)

    @staticmethod
    def __rename_key(old, new, dictionary):
        '''Rename a key in a dictionary.

        Arguments:
        old -- The old key name
        new -- The new key name
        dictionary -- The dictionary in which the key name should be changed
        '''
        if old in dictionary:
            dictionary[new] = dictionary.pop(old)
