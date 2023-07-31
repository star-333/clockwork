# MODULES
import click
import pyperclip
import re
from sys import platform
from zenlog import log
from typing import Callable

# CONSTANTS
SD2_COLOR = 'FFFFFF'



# TIMING CLASS
# contains the Timing class as well as various utility functions that have to do with timing.
class Timing:
    '''
    An offset / BPM / meter group. The offset is in milliseconds.

    - self.offset: float
    - self.bpm: float
    - self.meter: tuple[int, int]

    This class contains constructors, methods as well as various utility functions.
    '''

    def __init__(self, offset: float, bpm: float, meter: tuple[int, int] = (4,4)):
        self.offset = offset
        self.bpm = bpm
        self.meter = meter


    def __repr__(self):
        # print function
        return f'Timing / {str(self.offset)} / {str(self.bpm)} / {str(self.meter)}'


    @staticmethod
    def bpm(beat_length: float, round_result: bool = True) -> float:
        '''
        Takes a beat length in ms and returns the corresponding BPM

        - beat_length: float | a beat length in ms
        - round: bool | if True, round to a 0.001 precision. If false, do nothing.
        '''
        if round_result:
            return round(60000 / beat_length, 3)
        else:
            return 60000 / beat_length

    @staticmethod
    def beat_length(bpm: float, beat_amount: float | int = 1) -> float:
        '''
        Returns the length of one or more beats in ms.

        - bpm: float | BPM
        - beat_amount: float | the number of beats
        '''
        return (60000 / bpm) * beat_amount


    @staticmethod
    def beat_amount(bpm: float, duration: float) -> float:
        '''
        Takes a duration in ms and returns the corresponding amount of beats for a given BPM.

        - bpm: float | BPM
        - duration: float | a duration in ms
        '''
        return (duration * bpm) / 60000


    def get_offset_seconds(self) -> float:
        '''Returns the offset in seconds.'''
        return self.offset / 1000


    ### SOUNDODGER 2 ###
    # no from_sd2() constructor because Soundodger 2 does not store timing information in .xml files.

    def to_sd2(self, practice: bool = False) -> str:
        '''
        Returns a string containing a single soundodger bookmark with offset and BPM in its title.

        OPTIONAL PARAMETERS:
        - prac: bool | whether or not the bookmarks will be practice points
        '''
        time = str(self.get_offset_seconds())
        col = SD2_COLOR
        label = f'{time} / {str(self.bpm)}'
        
        if practice:
            prac = 'prac="True" '
        else:
            prac = ''

        return f'<Bookmark time="{time}" col="{col}" label="{label}" {prac}/>'

    
    ### OSU ###

    @classmethod
    def from_osu(cls, str_timing: str) -> Callable:
        '''
        Takes a single uninherited osu! timing and creates a single Timing instance from it.

        - timing: str | a string containing an uninherited osu! timing

        Please read the osu! documentation for more info: [https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)#timing-points]
        ''' 
        timing_data = str_timing.split(',')

        return cls(
            offset = float(timing_data[0]),
            bpm = cls.bpm(float(timing_data[1])),
            meter = (int(timing_data[2]), 4)
        )


    def to_osu(self, volume: int = 80, sample_set: int = 0, sample_index: int = 0) -> str:
        '''
        Returns a string containing a single uninherited osu timing.

        OPTIONAL ARGS:
        - volume: int | volume percentage for hit objects
        - sample_set: int | default sample set for hit objects
        - sample_index: int | custom sample index for hit objects

        Please read the osu! documentation for more info: [https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)#timing-points]
        '''
        time = str(round(self.offset))
        beat_length = str(self.beat_length(self.bpm))
        meter = str(self.meter[0])
        
        return f'{time},{beat_length},{meter},{sample_set},{sample_index},{volume},1,0'


    ### QUAVER ###

    @classmethod
    def from_quaver(cls, str_timing: str) -> Callable:
        '''
        Takes a single Quaver timing point and creates a single Timing instance from it.
        '''
        # split lines and strip unnecessary data
        timing_split = [s.strip('- ') for s in str_timing.split('\n')]
        # remove empty strings
        timing_split = [x for x in timing_split if x]
        # remove keys
        timing_split2 = [float(re.sub('[a-zA-Z: ]', '', s)) for s in timing_split]

        return cls(
            offset = timing_split2[0], 
            bpm = timing_split2[1]
        )


    def to_quaver(self) -> str:
        '''
        Returns a string containing a single Quaver timing.
        '''
        res = f'- StartTime: {self.offset}\n  Bpm: {self.bpm}\n'
        
        if self.meter != (4, 4):
            res += f'  Meter: {self.meter[0]}\n'

        return res



# TIMINGLIST CLASS
class TimingList():
    '''
    A collection of functions used for file formats which use beats instead of offsets.
    Constructor-like functions output list[Timing].
    '''
    
    ### STEPMANIA ###
    # supports .sm and .ssc

    @staticmethod
    def from_stepmania(offset: float, str_timings: list[str]) -> list[Timing]:
        '''
        Takes a list of Stepmania timing points and creates a list of Timing instances from it.
        Works with .sm and .ssc formats.
        NOTE: Only #BPMS is supported at the moment. #STOPS will be implemented in the future.

        - offset: float | the initial offset in seconds.
        - timings: list[str] | a list containing Stepmania timings (BPM changes)

        Please read the Stepmania documentation for more info: 
        [https://github.com/stepmania/stepmania/wiki/sm]
        [https://github.com/stepmania/stepmania/wiki/ssc]
        '''
        # convert the offset to milliseconds
        time = offset * 1000 
        res = []
        # turn the timings into usable data
        timings_split = [
            [float(val) for val in t.split('=')]
            for t in str_timings
        ]

        # i have no idea why this works
        res.append(Timing(time, timings_split[0][1]))
        
        for i in range(len(timings_split) - 1):

            current_bpm = timings_split[i][1]
            # add the time elapsed since the last bpm change
            time += Timing.beat_length(
                bpm = current_bpm,
                beat_amount = timings_split[i+1][0] - timings_split[i][0]
            )
            res.append(Timing(time, current_bpm))

        return res
        

    @staticmethod
    def to_stepmania(timings: list[Timing]) -> tuple[str, str]:
        '''
        Takes a list of Timing instances and returns a tuple of strings containing Stepmania #OFFSET and #BPM tags.
        Works with .sm and .ssc formats.
        NOTE: Only #BPMS is supported at the moment. #STOPS will be implemented in the future.

        - timings: list[Timing] | a list of Timing instances

        Please read the Stepmania documentation for more info: 
        [https://github.com/stepmania/stepmania/wiki/sm]
        [https://github.com/stepmania/stepmania/wiki/ssc]
        '''
        # offset
        offset_tag = f'#OFFSET:{timings[0].offset / 1000};'
        
        # header
        header_tag = '#BPMS:'
        total_beats = 0.0
        
        # create list of beats
        beat_list = [0.0]
        for i in range(1, len(timings)):         
            current_timing = timings[i]
        
            total_beats += Timing.beat_amount(current_timing.bpm, current_timing.offset - timings[i-1].offset)
            beat_list += [total_beats]
        
        # make header
        for i in range(len(beat_list)):
            header_tag += f'{beat_list[i]}={timings[i].bpm}\n,'

        header_tag = header_tag[:-1] + ';'

        return header_tag, offset_tag



if __name__ == '__main__':
    # test_data = [
    #     '0.000000=165.000000',
    #     '32.000000=160.000000',
    #     '33.000000=148.000000',
    #     '34.000000=131.000000',
    #     '36.000000=164.000000',
    #     '39.000000=169.000000',
    #     '40.500000=203.000000',
    # ]

    # fr = TimingList.from_stepmania(0.0, test_data)
    # log.debug(fr)

    # to = TimingList.to_stepmania(fr)
    # log.d(to)

    test_data = '''- StartTime: 2503\n  Bpm: 148.02000427246094\n'''

    fr = Timing.from_quaver(test_data)
    print(fr)
    to = fr.to_quaver()
    print(to)