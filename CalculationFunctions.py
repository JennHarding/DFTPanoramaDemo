
from music21 import stream, note, pitch, chord, meter
from numpy import array

import Corpus
from dftArrayClass import dft_array


def split_time_signature(numerator):
    """This is used to break down irregular time signatures (13/8, 11/4, etc.). It breaks the numerator of the time signature down into a combination of 3's and 2's. A numerator of 11 will return [3, 3, 3, 2], while a numerator of 5 will return [3, 2].

    Args:
        numerator (int): The top number in a time signature

    Returns:
        list: List of integers (only 3's and 2's) that sum to the original numerator
    """
    if numerator < 4:
        return [numerator]
    elif numerator == 4:
        return [2, 2]
    else: 
        return [3, *split_time_signature(numerator-3)]


def convert_time_signature(ts):
    ms = meter.MeterSequence(ts.ratioString)
    if ms.numerator in [2, 3, 4]:
        ms.partitionByCount(ms.numerator)
    else:
        partition_list = split_time_signature(ts.numerator)
        ms.partitionByList(partition_list)
    return ms


def get_beat_offsets_from_score(score):
    time_signature_list = []
    meter_sequence_list = []
    offset_list = [0]
    for m in score.semiFlat.getElementsByClass('Measure'):
        if m.timeSignature is not None:
            time_signature_list.append(m.timeSignature)
        else:
            time_signature_list.append(m.getContextByClass('TimeSignature'))
        
    for ts in time_signature_list:
        meter_sequence_list.extend(convert_time_signature(ts))
        
    duration_list = [m.duration for m in meter_sequence_list]

    for idx, i in enumerate(duration_list):
        offset_list.append(i.quarterLength + offset_list[idx])
    
    return offset_list


def update_array(array, note_, strategy, edo=12):
    if edo == 12:
        if strategy == 'Onset':
            array[note_.pitch.pitchClass] += 1
        elif strategy == 'Duration':
            array[note_.pitch.pitchClass] += note_.quarterLength
        elif strategy == 'Flat':
            array[note_.pitch.pitchClass] = 1
        return array 
        
         
def get_measure_number(score, offset):
    beat_measure_tuple = score.beatAndMeasureFromOffset(offset)
    measure_number = beat_measure_tuple[1].number
    return measure_number
    
    
def sliding_window(score, beat_offset_list, window_size, strategy, log=True, edo=12):
    """Collect the pc data from within a range (the window), convert that data to a dft_array class, then move the window over and do it again until the end of the piece/exerpt.

    Args:
        score (music21 Stream): The parsed score, now a music21 Stream object
        beat_offset_list (list): List of all offsets from the beginning of the score that coincide with beats
        window_size (integer): Length of the sliding window in beats
        strategy (string): Onset, duration, or flat
        log (bool, optional): Whether or not to apply logarithmic weighting to the pc content before applying the DFT. Defaults to True.
        edo (int, optional): Number of equal divisions of the octave. Defaults to 12.

    Returns:
        list: List of custom dftArrayClass arrays that represent pcsets that have had the DFT applied. Each array represents the pc content of one sliding window.
    """
    all_arrays = []
    for idx, window_begin in enumerate(beat_offset_list[:-window_size]):
        window_end = beat_offset_list[idx + window_size]
        current_array = array([0.0]*edo)
        measure1 = get_measure_number(score=score, offset=window_begin)
        
        if window_end == beat_offset_list[-1]:
            measure2 = get_measure_number(score=score, offset=beat_offset_list[-2])
        else:
            measure2 = get_measure_number(score=score, offset=window_end)
        
        for elem in score.semiFlat.getElementsByOffset(
            offsetStart=window_begin, 
            offsetEnd=window_end, 
            includeEndBoundary=False).getElementsByClass(['Note', 'Chord']):
            
            if isinstance(elem, chord.Chord):
                for a in elem.notes:
                    current_array = update_array(
                        array=current_array, 
                        note_=a, 
                        strategy=strategy,
                        edo=edo)
            elif isinstance(elem, note.Note):
                current_array = update_array(
                    array=current_array, 
                    note_=elem, 
                    strategy=strategy,
                    edo=edo)

        all_arrays.append(dft_array(
            array=current_array, 
            log_weight=log, 
            measure_range=(measure1, measure2)))
        
    return all_arrays


def score_to_data(config):  
    """This is the big, main function that takes us from the user inputs all the way to the numerical data.

    Args:
        config (tuple): Contains repertoire (string), excerpt (Boolean), measures (tuple with beginning and ending measures as integers), window size (integer), strategy (onset, duration, or flat), logarithmic weightning (Boolean), and edo (either 12 or 24)

    Returns:
        list: list of dft_array objects that represent pcsets that have had the DFT applied. Each dft_array represents the DFT of the pc content of one sliding window.
    """
     
    repertoire, measures, window, strat, log = config
    parsed_score = Corpus.parse_score(score_name=repertoire, measure_nums=measures)
    beat_offset_list = get_beat_offsets_from_score(score=parsed_score.parts[0])

    if strat == "Duration" or strat == "Flat":
        adjusted_score = parsed_score.sliceByBeat(addTies=False)
    else:
        adjusted_score = parsed_score.stripTies(retainContainers=True)
    
    multisets = sliding_window(
        score=adjusted_score, 
        beat_offset_list=beat_offset_list, 
        window_size=window, 
        strategy=strat, 
        log=log)

    return multisets