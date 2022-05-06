class ObjectCollection:

    def __init__(self, collection_name, member_types=None, init_members=None, restrictive=False):
        """This method takes the following positional parameter:

        - name (string): Name of the collection

        And the following keyword parameter:

        
        - member_types (list of types): List with which self.member_types_ is initialized. Its meaning depends on the value
        of self.fRestrictive_.
        - init_members (list of objects): The objects within init_members are candidates to be added to the new collection.
        They will end up belonging to the collection depending on self.fRestrictive_ and self.member_types_.
        - restrictive (scalar boolean): Initial value to give to self.fRestrictive_. While fRestrictive==False, all objects 
        regardless its type can be added to the collection. However, if fRestrictive_==True, only objects whose type belongs
        to self.member_types_ can be added to the collection.

        The aim of this class is to encapsule a set of objects under a certain name. The collection is also given an
        unique ID (an integer number).
        """

        if member_types is not None:
            if type(member_types)!=type([]):
                    print("In function ObjectCollection::__init__(): ERR0.")
                    return -1.
            else:        
                for i in range(len(member_types)):
                    if type(member_types[i])!=type(type(None)):
                        print("In function ObjectCollection::__init__(): ERR0.")
                        return -1.
            self.member_types_ = member_types
        else:
            self.member_types_ = []

        self.fRestrictive_ = restrictive
        self.fRestrictivenessIsLocked_ = False
        self.name_ = collection_name
        self.ID_ = self.get_new_ID()
        self.members_ = []
        if init_members is not None:
            if type(init_members)!=type([]):
                    print("In function ObjectCollection::__init__(): ERR2.")
                    return -1.
            else:
                for i in range(len(init_members)):
                        self.try_adding_an_element(init_members[i])

    def set_collection_name(self, new_name):
        self.name_ = new_name
        return

    def get_collection_name(self):
        return self.name_

    def get_restrictive(self):
        return self.fRestrictive_
        
    def lock_restrictiveness(self):
        """This method sets the flag self.fRestrictivenessIsLocked_ to True. Once that flag is set to True, the value of the 
        flag self.fRestrictive_ cannot be switched.
        """
        self.fRestrictivenessIsLocked_ = True
        return

    def switch_restrictiveness(self):
        """If the flag self.fRestrictivenessIsLocked_ is False, then this method switches the flag fRestrictive_. 
        Switching it from True to False causes no effect in any instance variable, apart from self.fRestrictive_. 
        Switching it from False to True automatically adds every type from self.members_ elements to self.member_types_.
        If the flag self.fRestrictivinessIsLocked_ is True, then this method does nothing."""

        if not self.fRestrictivenessIsLocked_:
            if self.fRestrictive_==False:
                for i in range(self.get_collection_size()):
                    if type(self.members_[i]) not in self.member_types_:
                        self.member_types_.append(type(self.members_[i]))

            self.fRestrictive_ = not self.fRestrictive_
        else:
            print("In function ObjectCollection::switch_restrictiveness():ERR0: Restrictiveness is locked. It cannot be switched.")
        return

    def get_collection_size(self):
        return len(self.members_)

    def try_adding_an_element(self, candidate_element):
        """This method tries to add candidate_element to the object collection. If fRestrictive_==False, the addition 
        is performed. If else, the addition is performed only if type(candidate_element) belongs to self.member_types_."""
        if self.fRestrictive_==False:
            self.members_.append(candidate_element)
        else:
            if type(candidate_element) in self.member_types_:
                self.members_.append(candidate_element)
            else:
                print("In function ObjectCollection::try_adding_an_element():ERR0: Could not add an element.")
                return
        return

    def print_collection(self):
        print("---- Element List ----")
        print("------ nº, Type ------")
        for i in range(self.get_collection_size()):
            print(i, ", ",  type(self.members_[i]))
        return
        
    next_id_ = 0
    @classmethod
    def get_new_ID(cls):
        cls.next_id_ += 1
        return cls.next_id_-1