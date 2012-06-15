import numpy
import quantities as qt
import mozaik.tools.units as munits
from mozaik.storage.queries import *
from mozaik.analysis.analysis_data_structures import StimulusDependentData
from neo.core.analogsignal import AnalogSignal
from neo.core.analogsignalarray import  AnalogSignalArray

def psth(spike_list,bin_length):
    """
    spike_list - should contain list of spiketrain objects.
    The function returns the psth of the spiketrains with bin length bin_length.
    
    bin_length - (ms) see spike_list explanation
    
    
    Note, the spiketrains are assumed to start and stop at the same time!
    """
    t_start = spike_list[0].t_start
    t_stop = spike_list[0].t_stop
    sampling_period = spike_list[0].sampling_period
    num_neurons = len(spike_list)
    num_bins = float((t_stop-t_start)/bin_length)
    
    h = []

    for i in xrange(0,num_neurons):
        h.append(numpy.histogram(spike_list[i], bins=num_bins, range=(float(t_start),float(t_stop)))[0] / (bin_length/1000))

    return AnalogSignalArray(numpy.transpose(numpy.array(h)),t_start=t_start,sampling_period=bin_length*qt.ms,units=munits.spike_per_sec)        
    
    
def psth_across_trials(spike_trials,bin_length):
    """
    spike_trials - should contain a list of lists of neo spiketrains objects, first coresponding to different trials
    and second to different neurons.  The function returns the histogram of spikes across trials with bin length bin_length
    Note, the spiketrains are assumed to start and stop at the same time.
    """
    return sum([psth(st,bin_length) for st in spike_trials])/len(spike_trials)


def spikes_to_StimulusDependentData(datastore,sheet_name,stimulus_type=None):
    """
    Creates StimulusDependentData data structure and loads it with spike_trains from 
    datastore that have been measured in sheet sheet_name and (optionally) to 
    stimulus type stimulus_type.
    """
    dsv = select_result_sheet_query(datastore,sheet_name)
    if stimulus_type != None:
       dsv = select_stimuli_type_query(dsv,stimulus_type)

    spikes = [seg.spiketrains for seg in dsv.get_segments()]
    st = [StimulusID(s) for s in dsv.get_stimuli()]
    return StimulusDependentData(spikes,st,sheet_name=sheet_name,analysis_algorithm="RawSpikeTrains")
