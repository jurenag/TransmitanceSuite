from ObjectCollection import ObjectCollection
from TransmitanceMeas1D import TransmitanceMeas1D

class TransmitanceMeas1DCollection(ObjectCollection):

    def __init__(self, collection_name, init_members=None):
        """This method takes the following compulsory parameter:

        - collection_name (string): It is passed to the base class initializer as collection_name.

        And the following optional parameter:

        - init_members (list of TransmitanceMeas1D objects): It is passed to the base class initializer
        as init_members.

        This class, which is derived from ObjectCollection class, is intended to represent a collection of
        TransmitanceMeas1D objects. The 
        """
        super().__init__(collection_name, member_types=[TransmitanceMeas1D], init_members=init_members, restrictive=True)
        self.lock_restrictiveness()
        return

    def get_list_of_members_data(self, retrieval_func_str):
        """This method gets the following compulsory parameter:
        
        - retrieval_func_str (string): This string must match the name of a TransmitanceMeas1D callable method with no 
        input parameters). Such method should provide the data which we want to accumulate in the goal list. Some examples 
        for this parameter are TransmitanceMeas::get_ref ("get_ref"), TransmitanceMeas::get_meas ("get_meas"), 
        TransmitanceMeas1D::get_rawest_ref ("get_rawest_ref"), TransmitanceMeas1D::get_rawest_meas ("get_rawest_meas") or 
        TransmitanceMeas1D::get_refInterpolator ("get_refInterpolator").
        
        Given a TransmitanceMeas1D method that takes no parameters, the aim of this method is to craft a list, datalist, 
        such that datalist[i]=self.members_[i].retrieval_func()."""

        list_of_members_data = []
        for i in range(len(self.members_)):
            exec("list_of_members_data.append(self.members_[i]." +retrieval_func_str+"())")
        return list_of_members_data
    
    def get_list_of_dep(self):
        """This method returns a list, datalist, so that datalist[i] stores the dependent variable data of the i-th 
        member of the collection."""
        return self.get_list_of_members_data("get_dep")

    def get_list_of_ref(self):
        """This method returns a list, datalist, so that datalist[i] stores the reference data of the i-th member
        of the collection."""
        return self.get_list_of_members_data("get_ref")

    def get_list_of_meas(self):
        """This method returns a list, datalist, so that datalist[i] stores the with-filter data of the i-th member
        of the collection."""
        return self.get_list_of_members_data("get_meas")

    def get_list_of_transmitance(self):
        """This method returns a list, datalist, so that datalist[i] stores the transmitance data of the i-th member
        of the collection."""
        return self.get_list_of_members_data("get_transmitance")

    def get_list_of_rawest_ref(self):
        """This method returns a list, datalist, so that datalist[i] stores the rawest available reference data of 
        the i-th member of the collection."""
        return self.get_list_of_members_data("get_rawest_ref")

    def get_list_of_rawest_meas(self):
        """This method returns a list, datalist, so that datalist[i] stores the rawest available with-filter data of 
        the i-th member of the collection."""
        return self.get_list_of_members_data("get_rawest_meas")

    def get_list_of_refInterpolator(self):
        """This method returns a list, datalist, so that datalist[i] stores the reference interpolator of the i-th 
        member of the collection."""
        return self.get_list_of_members_data("get_refInterpolator")

    @staticmethod
    def unzip_list(aList):
        """This function takes the following compulsory parameter:
        
        - aList (list of float bidimensional numpy arrays): Every array within the list must have length equal to 
        2 along the axis=1, i.e. two columns.
        
        This function returns two lists, c1_list and c2_list, so that c1_list[i] (resp. c2_list[i]) stores the first
        (second) column of aList[i]."""

        c1_list = [aList[i][:,0] for i in range(len(aList))]
        c2_list = [aList[i][:,1] for i in range(len(aList))]
        return c1_list, c2_list