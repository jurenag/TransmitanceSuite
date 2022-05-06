import numpy as np
import pandas as pd
from scipy import interpolate as spinter
from scipy import optimize as spopt

from TransmitanceMeas import TransmitanceMeas

class TransmitanceMeas1D(TransmitanceMeas):
    
    def __init__(self, ref, meas, ref_offset=0., meas_offset=0., dep=None, raw_ref=None, raw_meas=None, refInterpolator=None):
        """This method takes the following positional parameters:

        - self: Following the usual convention, this is the instance which is being created by means of __init__. It should not be
        explictly written when calling __init__.
        - ref (unidimensional float numpy array): Array of reference measurements. In this context, reference measurements 
        are those that are taken without filter.
        - meas (unidimensional float numpy array): Array of with-filter measurements. meas must have the same shape as reference.

        And the following keyword parameters:

        - ref_offset (scalar float) (resp. meas_offset):  This scalar is added to every entry in ref (meas) before computing
        the transmitance.
        - dep (unidimensional float numpy array): Values taken by a certain independent variable with regard to the provided data in ref 
        and meas. For example, when measuring transmitance as a function of the wavelength, dep would store the wavelength values for
        the provided data. If provided, dep must have the same shape as ref and meas.
        - raw_ref (resp. raw_meas) (bidimensional float numpy array): This parameter is internal to TransmitanceMeas1D. It is
        primarily used by class methods which eventually call this initializer. It is the raw reference (with-filter) measurements
        that were once provided to the calling class method, where raw_ref[:,0] (raw_meas[:,0]) are the dependent variable values 
        and raw_ref[:,1] (resp. raw_meas[:,1]) are the measurements themselves. Calls to this initializer from those alternative 
        constructors let raw_ref (raw_meas) be None if the input data was already point-wise compatible. In that case, self.raw_ref 
        (self.raw_meas) is set to be None. If else, the calling class methods are expected to provide the raw reference (with-filter) 
        data via this parameter and self.raw_ref (self.raw_meas) is set to raw_ref (raw_meas).
        - refInterpolator (callable with signature (float)): This parameter is internal to TransmitanceMeas1D. It is primarily used
        by class methods which eventually call this initializer. It is the interpolator which was built out of the available reference 
        data and that was used to craft a point-wise compatible set of measurements. Calls to this initializer from those alternative 
        constructors let refInterpolator be None if the input data was already point-wise compatible. Otherwise, they provide the
        used interpolator. However, if refInterpolator is not provided but dependent variable data is available, refInterpolator is
        built within this initializer. This is done for the sake of homogenizing across different instances of this class and making
        transmitance readout easier.

        This is the constructor to call if ref and meas are point-wise compatible, i.e. if for every entry position i, ref[i] 
        and meas[i] were measured under the same conditions (their ratio gives an actual transmitance).
        """

        if np.ndim(ref)!=1:
            print("In function TransmitanceMeas1D::__init__(): ERR0.")
            return -1.
            
        if np.shape(ref)!=np.shape(meas):
            print("In function TransmitanceMeas1D::__init__(): ERR1.")
            return -1.
            
        if dep is not None:
                if np.shape(ref)!=np.shape(dep):
                        print("In function TransmitanceMeas1D::__init__(): ERR2.")
                        return -1.
                        
        if raw_ref is None:
                self.raw_ref_ = None
        else:
                self.raw_ref_ = raw_ref
                
        if raw_meas is None:
                self.raw_meas_ = None
        else:
                self.raw_meas_ = raw_meas
            
        if refInterpolator is None:
            if dep is None:
                self.fInterpolator_=False #This flag is True (False) if an interpolator for reference measurements is (is not) available.
            else:
                self.fInterpolator_=spinter.CubicSpline(dep, ref)
                self.fInterpolator_=True
        else:
        	self.fInterpolator_=True
        	self.refInterpolator_=refInterpolator
        	
        super().__init__(ref, meas, ref_offset=ref_offset, meas_offset=meas_offset, dep=dep)
        return
        
    def get_rawest_ref(self):
    	if self.raw_ref_ is not None:
    	    return self.raw_ref_
    	else:
    	    return self.ref_
    	       
    def get_rawest_meas(self):
    	if self.raw_meas_ is not None:
    	    return self.raw_meas_
    	else:
    	    return self.meas_  
        
    def get_refInterpolator(self):
    	if self.fInterpolator_:
    		return self.refInterpolator_
    	else:
    		print("In function TransmitanceMeas1D::get_refInterpolator():ERR2: refInterpolator is not available.")
    		return

    @classmethod
    def from_ragged_data(cls, dep_ref, ref, dep_meas, meas, ref_offset=0., meas_offset=0., ref_ref_func=None):
        """This class method is aimed at instantiating the TransmitanceMeas1D class by handling the particular case of ragged 
        input data, namely, the case where the number of taken reference measurement is different from the number of w/f 
        measurements. In this case, to relate ref measurements with w/f measurements (p.e. via interpolation), the dependent 
        variable values are necessary. This situation is usual when scanning a filter wavelength-wise consecutive times with the 
        same light source. In that case, you could save some time just by measuring the light source spectrum as precisely as you 
        want for the first time, and never repeating those reference measurements, at least not with that fine sample of 
        wavelengths. In that case, you would want to repeat some reference measurements just to see if the overall light source 
        spectrum has been scaled due to long functioning periods of time. (Indeed, for the same lamp at different times, typically 
        you wouldn't expect shape changes in the spectrum, but overall scaling.) This class method takes the following positional 
        parameters:

        - dep_ref (unidimensional float numpy array): Values for the dependent variable of reference measurements.
        - ref (unidimensional float numpy array): Reference measurements.
        - dep_meas (unidimensional float numpy array): Values for the dependent variable of with-filter measurements.
        - meas (unidimensional float numpy array): With-filter measurements.

        And the following keyword parameters:

        - ref_offset (scalar float) (resp. meas_offset):  This scalar is added to every entry in ref (meas) before computing
        the transmitance.
        - ref_ref_func (callable with signature (float)): If provided, this is the function to fit to the set of ref measurements 
        by vertical offsetting and scaling (in that order).

        The goal of this class method is to craft a point-wise compatible set of ref and meas points based on the input ragged data, 
        thus surpassing the bottleneck of class TransmitanceMeas to compute the transmitance. To do so, at some point this method
        must craft a float function with float input which is later used to guess the reference measurements in every point
        within dep_meas (i.e. a reference measurements interpolator). To create this function, this class method can follow two 
        alternative ways depending on whether ref_ref_func is provided or not. If it is not provided, then the reference measurements are 
        interpolated (or extrapolated) in every point within dep_meas by using scipy.interpolate.CubicSpline, which is constructed via 
        (dep_ref, ref). If it is provided, then the desired function is created by fitting ref_ref_func to the available set of reference
        measurements, (dep_ref, ref). In this case, the fitting function is f(x) = scaling*(v_offest+ref_ref_func(x)), where 
        scaling and v_offset are the free parameters.  
        """

        aux = type(np.array([]))
        if aux!=type(dep_ref) or aux!=type(ref) or aux!=type(dep_meas) or aux!=type(meas):
            print("In function TransmitanceMeas1D::from_ragged_data(): ERR0.")
            return -1.            

        if np.ndim(dep_ref)!=1 or np.ndim(ref)!=1 or np.ndim(dep_meas)!=1 or np.ndim(meas)!=1:
            print("In function TransmitanceMeas1D::from_ragged_data(): ERR1.")
            return -1.

        if np.shape(dep_ref)!=np.shape(ref) or np.shape(dep_meas)!=np.shape(meas):
            print("In function TransmitanceMeas1D::from_ragged_data(): ERR2.")
            return -1.

        raw_dep_ref	= dep_ref
        raw_ref	= ref +ref_offset

        if ref_ref_func is None:
            ref_func = spinter.CubicSpline(raw_dep_ref, raw_ref)
        else:
            fitting_func = lambda x, sca, off: sca*(off+ref_ref_func(x))
            popt, _ = spopt.curve_fit(fitting_func, raw_dep_ref, raw_ref)
            ref_func = np.vectorize(lambda x: popt[0]*(popt[1]+ref_ref_func(x)))
        
        dep     = dep_meas
        meas    = meas +meas_offset
        ref     = ref_func(dep)
        
        raw_ref 	= cls.stick_together(raw_dep_ref, raw_ref, axis=1)
        raw_meas 	= cls.stick_together(dep, meas)
        
        return cls(ref, meas, ref_offset=0., meas_offset=0., dep=dep, raw_ref=raw_ref, raw_meas=raw_meas, refInterpolator=ref_func) #Offsets have already been applied

    @classmethod
    def from_files(cls, ref_filepath, meas_filepath, ref_ref_filepath=None, **parsing_arguments):
        """This class method is aimed at instantiating the TransmitanceMeas1D class when providing the data files which store
        the information regarding the reference measurements and with-filter measurements. This class method is strongly dependent
        on the format of the input files. This method uses the static method default_parser, which has been written according to 
        the format that we are currently using at IFIC to store the Keithley readout (Jose's labview app). See default_parser
        documentation (*) for further information on this format. This class method takes the following positional parameters:

        - ref_filepath (string): Filepath for the file which stores the reference measurements.
        - meas_filepath (string): Filepath for the file which stores the with-filter measurements.

        And the following keyword parameters:

        - ref_ref_filepath (string): Filepath for the file which stores the reference measurements data to use in order to
        fit the light source dependence given in ref_filepath.

        To fulfill its goal, this class method parses the input filepaths and determines whether the provided data is compatible, 
        i.e. there's the same amount of ref and meas points, and they are taken at the same values of the dependent variable.
        If so, this method directly calls the initializer of the class. If not, this method relies on classmethod from_ragged_data.
        For further information, inspect the documentation of those methods.
        """

        dep_ref, ref    = cls.default_parser(ref_filepath)
        dep_meas, meas  = cls.default_parser(meas_filepath)
        
        compatible = False
        if np.shape(dep_ref)[0]==np.shape(dep_meas)[0]:
            if np.prod(dep_ref==dep_meas):
                compatible = True

        if compatible == False:
            if ref_ref_filepath is not None:
                dep_ref_ref, ref_ref = cls.default_parser(ref_ref_filepath)
                ref_ref_func    = spinter.CubicSpline(dep_ref_ref, ref_ref)
                return cls.from_ragged_data(dep_ref, ref, dep_meas, meas, ref_offset=0., meas_offset=0., ref_ref_func=ref_ref_func) #Offsets have already been applied
            else:
                return cls.from_ragged_data(dep_ref, ref, dep_meas, meas, ref_offset=0., meas_offset=0.) #Offsets have already been applied
        else:
            return cls(ref, meas, ref_offset=0., meas_offset=0., dep=dep_ref, refInterpolator=None, raw_ref=None, raw_meas=None)

    @staticmethod
    def default_parser(filepath, x_col=3, y_col=1, separator="\t"):
        """Parsers are meant to recieve a filepath and any necessary keyword argument, and output two float unidimensional
        numpy arrays. Such filepath is supossed to store a certain set of points. The first array returned by the parser
        matches the x-values, whereas the second one matches the y-values of the set of points. This parser is designed to 
        properly parse the format that we are are currently using at IFIC to store the keithley readout with Jose's labview
        app.
        
        (*) The format of the files provided to this function must match the following one. The first row of the file is
        a headers row. Its content does not matter since this row is going to be ignored. The rest of the rows contain
        4 columns, which are, from left to right: the time stamp of the measurement, the average, the STD and the wavelength.
        The file's second row contains the data regarding a dark current measurement. There's no defined wavelength for this
        measurement. The fourth field of this row normally contains "DC", for dark current. Such field is ignored. The value
        for the dark current is positive. Note that DC>0, but it should be subtracted from the available data. This is inherent
        to this format and is handled by this method. Columns are separated by tabulators ("\t").

        """

        data = np.array(pd.read_csv(filepath, header=None, sep=separator, skiprows=1))
        offset = data[0,1]
        data = data[1:,:]
        data[:,y_col] -= offset #The DC is subtracted
        data[:,x_col] = np.vectorize(float)(data[:,x_col]) #The "DC" entry makes pandas interpret the whole column as string
        data = TransmitanceMeas1D.sort_bidimensional_array_mutually(data, axis=0, line=x_col) #Sort the data x-values-wise (necessary for further interpolation)
        return data[:,x_col], data[:,y_col]

    @staticmethod
    def sort_bidimensional_array_mutually(bid_array, axis=0, line=0):
        """This static method gets:
        - bid_array (bidimensional float numpy array): Array to be sorted.
        - axis (scalar integer, 0 or 1): Axis along which the sort must be done.
        - line (scalar integer): If axis=0 (resp. axis=1), the iterator value for the column (row) according to which bid_array 
        must be sorted.
        
        This function returns a sorted copy of bid_array. If axis=0 (resp. axis=1), bid_array columns (rows) are conveniently 
        switched so that bid_array[:,line] (bid_array[line, :]) is sorted. Note that the sorting process treat columns (rows) as 
        indivisible packages.
        """

        if axis!=0 and axis!=1:
            print("In function sort_bidimensional_array_mutually(): Not allowed value for axis. Returning -1.")
            return -1.
        if line<0:
            print("In function sort_bidimensional_array_mutually(): Not allowed value for line. Returning -1.")
            return -1.
        if axis==0 and line>=np.shape(bid_array)[0]:
            print("In function sort_bidimensional_array_mutually(): Not allowed value for line. Returning -1.")
            return -1.
        if axis==1 and line>=np.shape(bid_array)[1]:
            print("In function sort_bidimensional_array_mutually(): Not allowed value for line. Returning -1.")
            return -1.

        sorted_array = bid_array
        iterator = list(range(np.shape(bid_array)[not axis]))
        
        if axis==0:   
            sorting_indices = np.argsort(bid_array[:, line])
            for i in iterator:
                sorted_array[:, i] = sorted_array[sorting_indices, i]
        
        else:
            sorting_indices = np.argsort(bid_array[line, :])
            for i in iterator:
                sorted_array[i, :] = sorted_array[i, sorting_indices]

        return sorted_array
        
    @staticmethod
    def stick_together(arr1, arr2, axis=0):
        """This function takes:
        - arr1 (resp. arr2) (unidimensional or bidimensional float numpy array): Array to concatenate.
        - axis (scalar boolean): This parameter labels an axis among 0 or 1, where 0==False and 1==True.
        
        This equation returns a new array which results from sticking arr1 and arr2 together along axis=axis.
        Note the following natural compatibility requirements. For bidimensional arrays, arr1 and arr2 must have the same length along 
        the axis equal to (not axis). For one unidimensional array, say arr1, and one bidimensional array, say arr2, the length of 
        numpy.expand_dims(arr1, axis=axis) along (not axis) must equal the length of arr2 along not axis. For two unidimensional arrays, 
        the expansion of both arrays along axis=not axis must have the same length.
        """
        
        if type(arr1)!=type(np.array([])) or type(arr2)!=type(np.array([])):
            print("In function TransmitanceMeas1D::stick_together(): ERR0.")
            return -1.
        if np.ndim(arr1)>2 or np.ndim(arr2)>2:
            print("In function TransmitanceMeas1D::stick_together(): ERR1.")
            return -1.
        
        prod = np.ndim(arr1)*np.ndim(arr2)
        if prod==4:
            if np.shape(arr1)[not axis]!=np.shape(arr2)[not axis]:
                print("In function TransmitanceMeas1D::stick_together(): ERR2.")
                return -1.    
            else:
                return np.concatenate((arr1, arr2), axis=axis)
        elif prod==2:
            if np.ndim(arr1)==1:
                unid_array=arr1
                bid_array=arr2
            else:
                unid_array=arr2
                bid_array=arr1
            
            if np.shape(unid_array)[0]!=np.shape(bid_array)[not axis]:
                print("In function TransmitanceMeas1D::stick_together(): ERR3.")
                return -1.
            else:
                unid_array = np.expand_dims(unid_array, axis=axis)
                return np.concatenate((unid_array, bid_array), axis=axis)
        else:
            if np.shape(arr1)[0]!=np.shape(arr2)[0]:
                print("In function TransmitanceMeas1D::stick_together(): ERR4.")
                return -1.
            else:
                arr1 = np.expand_dims(arr1, axis=axis)
                arr2 = np.expand_dims(arr2, axis=axis)
                return np.concatenate((arr1, arr2), axis=axis)
