# MODULES
import click
import pyperclip
from decimal import *
from sys import platform
from zenlog import log
from typing import Callable

# CONSTANTS
SD2_COLOR = 'FFFFFF'
STEP128 = Decimal('0.0078125')

# DECIMAL CONTEXT
# for 1/128 subdivisions. fuck 1/192ths they don't translate well into decimals
getcontext().prec = 7



# UTILS
def quantize_value(val: Decimal, step: Decimal):
    '''
    Quantizes a given value based on step size.

    - val: Decimal | the value to quantize.
    - step: Decimal | the step size to use.
    '''
    return round(val / step, 0) * step



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

    def __init__(self, offset: Decimal, bpm: Decimal, meter: tuple[int, int] = (4,4)):
        self.offset = offset
        self.bpm = bpm
        self.meter = meter


    def __repr__(self):
        # print function
        return f'Timing / {str(self.offset)} / {str(self.bpm)} / {str(self.meter)}'


    @staticmethod
    def bpm(beat_length: Decimal, round_result: bool = True) -> Decimal:
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
    def beat_length(bpm: Decimal, beat_amount: Decimal | int = 1) -> Decimal:
        '''
        Returns the length of one or more beats in ms.

        - bpm: float | BPM
        - beat_amount: float | the number of beats
        '''
        return (60000 / bpm) * beat_amount


    @staticmethod
    def beat_amount(bpm: Decimal, duration: Decimal) -> Decimal:
        '''
        Takes a duration in ms and returns the corresponding amount of beats for a given BPM.

        - bpm: float | BPM
        - duration: float | a duration in ms
        '''
        return (duration * bpm) / 60000


    def get_offset_seconds(self) -> Decimal:
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
    def from_osu(cls, osu_timing: str) -> Callable:
        '''
        Takes a single uninherited osu! timing and creates a single Timing instance from it.

        - timing: str | a string containing an uninherited osu! timing

        Please read the osu! documentation for more info: [https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)#timing-points]
        ''' 
        timing_data = osu_timing.split(',')

        return cls(
            offset = Decimal(timing_data[0]),
            bpm = cls.bpm(Decimal(timing_data[1])),
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
    def from_quaver(cls, qua_timing: str) -> Callable:
        '''
        Takes a single Quaver timing point and creates a single Timing instance from it.
        '''
        # split lines and strip unnecessary data
        timing_data = [s.strip('- ') for s in qua_timing.split('\n')]
        # remove empty strings
        timing_data = [s.split(':') for s in timing_data if s]
        # convert to dict (easier to work with)
        timing_dict = {
            x[0]: x[1].strip(' ')
            for x in timing_data
        }

        # meter
        if 'Meter' not in timing_dict:
            meter_denominator = 4
        elif timing_dict['Meter'] == 'Triple':
            meter_denominator = 3
        else:
            meter_denominator = int(timing_dict['Meter'])
        
        return cls(
            offset = Decimal(timing_dict['StartTime']),
            bpm = Decimal(timing_dict['Bpm']),
            meter = (meter_denominator, 4)
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
    def from_stepmania(offset: Decimal, sm_timings: list[str]) -> list[Timing]:
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
        time = Decimal(offset * 1000)
        res = []
        # turn the timings into usable data
        timings_split = [
            [Decimal(val) for val in t.split('=')]
            for t in sm_timings
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
    def to_stepmania(timings: list[Timing], step: Decimal = STEP128) -> tuple[str, str]:
        '''
        Takes a list of Timing instances and returns a tuple of strings containing Stepmania #OFFSET and #BPM tags.
        Works with .sm and .ssc formats.
        NOTE: Only #BPMS is supported at the moment. #STOPS will be implemented in the future.

        - timings: list[Timing] | a list of Timing instances
        - precision: Decimal | the step of the beat offset quantization. 
            In some cases, a smaller step is preferrable, but in some others, you might be better off using 1/2nds or whole beats.

        Please read the Stepmania documentation for more info: 
        [https://github.com/stepmania/stepmania/wiki/sm]
        [https://github.com/stepmania/stepmania/wiki/ssc]
        '''
        # offset
        offset_tag = f'#OFFSET:{timings[0].offset / 1000};'
        
        # header
        header_tag = '#BPMS:'
        total_beats = Decimal('0.0')
        
        # create list of beats
        beat_list = [Decimal('0.0')]
        for i in range(1, len(timings)):
            current_timing = timings[i]
        
            total_beats += quantize_value(
                Timing.beat_amount(timings[i-1].bpm, (current_timing.offset - timings[i-1].offset)),
                step
            )
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

    # test_data = '''StartTime: 2503\n Bpm: 148.02000427246094\n     Meter: 4\n'''

    # fr = Timing.from_quaver(test_data)
    # print(fr)
    # to = fr.to_quaver()
    # print(to)

    pass