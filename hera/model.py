# Author: Lukas Halbritter <halbritl@informatik.uni-freiburg.de>
# Copyright 2019
'''This module provides the functionality to build hera models.'''
import json

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
        model_dict = {
            'description': self.__description,

            'actions': self.__actions,
            'background': self.__background,
            'consequences': self.__consequences,

            'mechanisms': self.__mechanisms,
            'utilities': self.__utilities,
            'intentions': self.__intentions,
            }

        return json.dumps(model_dict, indent=4)

    def reset(self):
        '''Reset the model.
        Clear all lists and dictionaries, only the description stays unchanged.
        '''
        for var in vars(self):
            attr = getattr(self, var)
            if isinstance(attr, list) or isinstance(attr, dict):
                attr.clear()

    # DESCRIPTION --------------------------------------------------------------
    def set_description(self, description):
        '''Set the description of the model.

        Arguments:
        description -- A string that describes the model.
        '''
        self.__verify_description(description)

        self.__description = description

    def get_description(self):
        '''Get the description of the model.'''
        return self.__description

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
        This also removes the utilities of this action and mechanism, where the
        action took part of, from the model to keep the model consistent.

        Arguments:
        *actions -- One or multiple strings that represent action names.
        '''
        for action in actions:
            # If the action exists, remove it from the model.
            # Else, skip further deletions
            if action in self.__actions:
                self.__actions.remove(action)
            else:
                continue

            # Remove the intentions of the action from the model.
            del self.__intentions[action]

            # TODO: Update mechanisms which contain the action CHECK
            for consequence in self.__consequences:
                # If action is part of a mechanism, remove mechanism.
                if "'{}'".format(action) in self.__mechanisms[consequence]:
                    self.__mechanisms[consequence] = []

    def rename_action(self, action_old, action_new):
        '''Renames action and changes the action name accordingly in
        mechanism and intentions containing that action.

        Arguments:
        action_old -- Old action name.
        action_new -- New action name.
        '''

        if (self.__verify_action(action_old, True) and
                self.__verify_action(action_new)):
            self.__actions.remove(action_old)
            self.__actions.append(action_new)

        # Rename action within mechanism.
        for consequence in self.__consequences:
            # If action is part of a mechanism, rename action within.
            if "'{}'".format(action_old) in self.__mechanisms[consequence]:
                self.__mechanisms[consequence].remove("'{}'".format(action_old))
                self.__mechanisms[consequence].append("'{}'".format(action_new))

        # Rename action within intentions.
        self.__intentions[action_old].remove(action_old)
        self.__intentions[action_old].append(action_new)
        self.__intentions[action_new] = self.__intentions[action_old]
        del self.__intentions[action_old]

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
            if not isinstance(bg_condition, str):
                raise TypeError('A background condition name must be a string.')

            # Add the background condition to the background list
            if bg_condition not in self.__background:
                self.__background.append(bg_condition)

    def remove_background(self, *background):
        '''Remove one or more background conditions from the model.
        If there is no such background condition in the model, this will be
        ignored.

        Arguments:
        *background -- One or multiple strings that represent background
                       conditions.
        '''
        for bg_condition in background:
            # If the condition exists, remove it from the model.
            # Else, skip further deletions
            if bg_condition in self.__background:
                self.__background.remove(bg_condition)
            else:
                continue

            # TODO: Update mechanisms which contain the background CHECK
            for consequence in self.__consequences:
                # If background is part of a mechanism, remove mechanism.
                if "'{}'".format(bg_condition) in self.__mechanisms[consequence]:
                    self.__mechanisms[consequence] = []

    def rename_background(self, bg_old, bg_new):
        '''Renames background and changes the background name accordingly in
        mechanism containing that background.

        Arguments:
        bg_old -- Old background name.
        bg_new -- New background name.
        '''

        if self.__verify_background(bg_old, check_if_in_model=True) and \
            self.__verify_background(bg_new):
            self.__background.remove(bg_old)
            self.__background.append(bg_new)

        # Rename backround within mechanism.
        for consequence in self.__consequences:
            # If background is part of a mechanism, rename background within.
            if "'{}'".format(bg_old) in self.__mechanisms[consequence]:
                self.__mechanisms[consequence].remove("'{}'".format(bg_old))
                self.__mechanisms[consequence].append("'{}'".format(bg_new))

    # CONSEQUENCES -------------------------------------------------------------
    def add_consequences(self, *consequences):
        '''Add one or more consequences to the model.
        If the consequence is already in the list, it will not be added twice.

        Arguments:
        *consequences -- One or multiple strings that represent consequences.
        '''
        for consequence in consequences:
            # Assure that the consequence is a string
            if not isinstance(consequence, str):
                raise TypeError('A consequence name must be a string.')

            # If it does not already exists, add the consequence to the list
            if consequence not in self.__consequences:
                self.__consequences.append(consequence)

            # Instantiate the mechanisms of the consequences with empty
                # mechanism
                self.__mechanisms[consequence] = [] #TODO CHECK

    def remove_consequences(self, *consequences):
        '''Remove one or multiple consequences from the model.
        This also removes the mechanisms and utilites of the consequences.
        Intentions which contain the consequences are updated as well.

        Arguments:
        *consequences -- One or more strings which represent the consequence
                         names.
        '''
        for consequence in consequences:
            # If the consequence exists, remove it from the model.
            # Else, skip further deletions
            if consequence in self.__consequences:
                self.__consequences.remove(consequence)
            else:
                continue

            # TODO: Update mechanisms which contain the consequence CHECK
            # If consequence is part of a mechanism, delete mechanism.
            if "'{}'".format(consequence) in self.__mechanisms[consequence]:
                del self.__mechanisms[consequence]

            # Remove the utilities of the consequence from the model
            for cons_string in [consequence, self.__not_string(consequence)]:
                if cons_string in self.__utilities:
                    del self.__utilities[consequence]

            # Remove the consequence from all intentions
            for intentions in self.__intentions.items():
                if consequence in intentions:
                    intentions.remove(consequence)

    def rename_consequence(self, con_old, con_new):
        '''Renames consequence and changes the consequence name accordingly in
        mechanisms, utilities and intentions containing that consequence.

        Arguments:
        con_old -- Old consequence name.
        con_new -- New consequence name.
        '''

        if self.__verify_consequence(con_old, check_if_in_model=True) and \
            self.__verify_consequence(con_new):
            self.__consequences.remove(con_old)
            self.__consequences.append(con_new)

        # Rename consequence within mechanism.
        for consequence in self.__consequences:
            # If consequence is part of a mechanism, rename consequence within.
            if "'{}'".format(con_old) in self.__mechanisms[consequence]:
                self.__mechanisms[consequence].remove("'{}'".format(con_old))
                self.__mechanisms[consequence].append("'{}'".format(con_new))
        self.__mechanisms[con_new] = self.__mechanisms[con_old]
        del self.__mechanisms[con_old]

        # Rename consequence within utilities.
        self.__utilities[con_new] = self.__utilities[con_old]
        del self.__utilities[con_old]

        # Rename consequence within intentions.
        for action in self.__actions:
            if con_old in self.__intentions[action]:
                self.__intentions[action].remove(con_old)
                self.__intentions[action].append(con_new)

    # MECHANISMS ---------------------------------------------------------------
    def add_mechanism(self, consequence, *mechanism):
        '''Add one or more variables to the mechanism of a consequence.
        If the variable is already in the list, it will not be added twice.

        Arguments:
        consequence -- The consequence for which the mechanism should be added.
        *mechanism -- One or multiple strings that represent a mechanism.
        '''
        self.__verify_consequence(consequence, True)

        # Assure that the variables are all valid (exist in the model).
        for variable in mechanism:
            var_valid = []
            var_valid.append(variable in self.__actions)
            var_valid.append(variable in self.__background)
            var_valid.append(variable in self.__consequences)
            if not any(var_valid):
                raise TypeError('The components of a mechanism ' +
                                'must be part of the model.')
            else:
            # If it does not already exists, add the variable to the list.
                if variable not in self.__mechanisms[consequence]:
                    self.__mechanisms[consequence].append("'{}'".format(variable))

        # OLD: might still be useful, do not delete yet
        # mecha = []
        # if "And" in self.__mechanisms[consequence]:
        #     mecha=self.__mechanisms[consequence][5:-2].split('\',\'')
        # elif self.__mechanisms[consequence]!=[]:
        #     mecha.append(self.__mechanisms[consequence])

        #for variable in mechanism:
        #    # If the variable is not already in the mechanism,
        #    # add it
        #    if variable not in self.__mechanisms[consequence]:
        #        mecha.append(variable)
        #self.__mechanisms[consequence]=self.__and_string(mecha)

    def remove_mechanism(self, consequence, *mechanism):
        '''Remove one or more intended variables of the mechanism of a
        consequence.

        Arguments:
        consequence -- The consequence for which (parts of) the mechanism
        should be removed.
        *mechanism -- The (part of the) mechanism to be removed.
        '''
        self.__verify_consequence(consequence, True)

        for variable in mechanism:
            if "'{}'".format(variable) in self.__mechanisms[consequence]:
                self.__mechanisms[consequence].remove("'{}'".format(variable))
            else:
                continue

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
        # Assure that the value of the utility is an integer
        if not isinstance(value, int):
            raise TypeError('The utility of a consequence must be an integer '
                            + 'value.')

        self.__verify_consequence(consequence, True)

        # Adjust the consequence name if the utility of not reaching the
        # consequence is to be set
        if not affirmation:
            consequence = self.__not_string(consequence)

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
        if not affirmation:
            consequence = self.__not_string(consequence)

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
            if consequence not in self.__intentions[action]:
                self.__intentions[action].append(consequence)

    def remove_intentions(self, action, *consequences):
        '''Remove one or more intended consequences of an action.
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

    def check_model(self):
        # TODO: Check if all consequences can be reached CHECK
        '''Checks if all consequences can be reached (mechanism exists).'''
        for consequence in self.__consequences:
            if self.__mechanisms[consequence] == []:
                # TODO: What error type is appropriate?
                raise RuntimeError("Missing mechanism for consequence.")


    # STRING MODIFIERS ---------------------------------------------------------
    @staticmethod
    def __not_string(variable):
        return 'Not(\'' + variable + '\')'

    # PRIVATE HELPER METHODS ---------------------------------------------------
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

    def __check_type(self, obj, obj_type, error_msg):
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

    def __check_if_in_model(self, obj, obj_list, obj_name):
        '''Raise a KeyError, if a given object is not in a given list.

        Argumens:
        obj -- The object in question
        obj_list -- The list in which the object should be
        obj_name -- The name of the object (used to generate the error message
                    printed by the KeyError)
        '''
        if obj not in obj_list:
            raise KeyError('{} is no {} of the model.'.format(obj, obj_name))
