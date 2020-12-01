import numpy as np


class dft_array(object):
    """DFT array object.

    Args:
        array (list): List that indicates the number of each pc present
        measure_range (tuple, optional): Beginning and ending measure of window as integers. Defaults to None.
        log_weight (bool, optional): Determines whether logarithmic weighting is applied. Defaults to True.
    """

    def __init__(self, array, measure_range=None, log_weight=True):

        self.original_array = array
        self.measure_range = measure_range
        if measure_range is not None:
            self.start_measure = measure_range[0]
            self.end_measure = measure_range[1]
        self.log_weight = log_weight
        self.edo = len(self.original_array)
    
    def do_dft(self):
        if self.log_weight is True:
            return np.fft.fft(np.log2(self.original_array + 1))
        else:
            return np.fft.fft(self.original_array)
    
    def mag_dict(self):
        return {f'f{i}' : np.abs(self.do_dft())[i] for i in range(0, self.edo//2 + 1)}
    
    def phase_dict(self):
        return {f'f{i}' : int(np.around(np.angle(self.do_dft(), deg=True)[i])) for i in range(1, self.edo//2 + 1)}
    
    def rounded_weighted_array(self):
        return np.around(np.log2(self.original_array + 1), decimals=2)
    
    def rounded_original_array(self):
        return np.around(self.original_array, decimals=2)
    