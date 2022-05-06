import numpy as np

class TransmitanceMeas:
    
    def __init__(self, ref, meas, ref_offset=0., meas_offset=0., dep=None):
        """This method takes the following positional parameters:

        - self: Following the usual convention, this is the instance which is being created by means of __init__. It should not be
        explictly written when calling __init__.
        - ref (float numpy array): Array of reference measurements. In this context, reference measurements are those that
        are taken without filter.
        - meas (float numpy array): Array of with-filter measurements. meas must have the same shape as reference. 

        And the following optional parameters:

        - ref_offset (scalar float) (resp. meas_offset):  This scalar is added to every entry in ref (meas).
        - dep (float numpy array): Values taken by a certain independent value with regard to the provided data in ref and meas.
        For example, when measuring transmitance as a function of the wavelength, dep would store the wavelength values for
        the provided data. If provided, dep must have the same shape as ref and meas.
        
        This is the constructor to call if for every entry position pos=(i_1, i_2, ..., i_n), ref[pos] and meas[pos] were
        measured under the same conditions, i.e. their ratio gives an actual transmitance.
        """

        if type(np.array([]))!=type(ref) or type(np.array([]))!=type(meas):
            print("In method TransmitanceMeas::__init__(): ERR0.")
            return -1.

        if np.shape(ref)!=np.shape(meas):
            print("In method TransmitanceMeas::__init__(): ERR1.")
            return -1.

        self.dep_is_available_ = False

        if dep is not None:
            if np.shape(dep)!=np.shape(ref):
                print("In method TransmitanceMeas::__init__(): ERR2.")
                return -1.  
            else:
                self.dep_ = dep
                self.dep_is_available_ = True

        self.ref_    = ref  +ref_offset
        self.meas_   = meas +meas_offset
        return

    def get_dep(self):
        if self.dep_is_available_:
            return self.dep_
        else:
            print("In function TransmitanceMeas::get_dep(): Dependent variable information is not available.")
            return None

    def get_ref(self):
        return self.ref_

    def get_meas(self):
        return self.meas_

    def correct_ref(self, offset):
        """This method takes:
        - offset (scalar float)
        This function adds> offset to every entry in self.ref."""
        self.ref_ += offset
        return

    def correct_meas(self, offset):
        """This method takes:
        - offset (scalar float)
        This function adds offset to every entry in self.meas."""
        self.meas_ += offset
        return

    def check_compatibility(self):
        """There are different ways to instantiate this class, i.e. different ways of providing the reference and the
        with-filter data. (Maybe not in this class, but in subclasses that inherit from this one). At some point before 
        computing the actual transmitance you have to make sure that your data is point-wise compatible, i.e. that you got 
        one reference entry for each with-filter measurement. This bottleneck is implemented by this function, which is 
        called from compute_transmitance() before actually computing the transmitance."""
        if self.dep_is_available_:
            return np.shape(self.ref_)==np.shape(self.meas_) and np.shape(self.ref_)==np.shape(self.dep_)
        else:
            return np.shape(self.ref_)==np.shape(self.meas_)

    def get_transmitance(self):
        """This method computes the transmitance out of self.ref and self.meas."""

        if self.check_compatibility():
            self.transmitance_ = self.meas_/self.ref_
            return self.transmitance_
        else:
            print("In function TransmitanceMeas::get_transmitance(): ERR0.")
            return -1.
