# MODULES
import click
import pyperclip
from sys import platform
from zenlog import log

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
        return f'BpmOffset / {str(self.offset)} / {str(self.bpm)} / {str(self.meter)}'


    @staticmethod
    def to_bpm(beat_length: float) -> float:
        '''Takes a beat length in ms and returns the corresponding BPM'''
        return round(60000 / beat_length, 3)


    def get_beat_length(self) -> float:
        '''Returns the length of a corresponding beat in ms.'''
        return 60000 / self.bpm


    def get_seconds(self) -> float:
        '''Returns the offset in seconds.'''
        return self.offset / 1000


    ### SOUNDODGER 2 ###
    # contains no from_sd2() constructor because Soundodger 2 does not store timing information in .xml files.

    def to_sd2(self, practice: bool = False) -> str:
        '''
        Returns a string containing a single soundodger bookmark with offset and BPM in its title.

        OPTIONAL PARAMETERS:
        - prac: bool | whether or not the bookmarks will be practice points
        '''
        time = str(self.get_seconds())
        col = SD2_COLOR
        label = f'{time} / {str(self.bpm)}'
        
        if practice:
            prac = 'prac="True" '
        else:
            prac = ''

        return f'<Bookmark time="{time}" col="{col}" label="{label}" {prac}/>'

    
    ### OSU ###

    @classmethod
    def from_osu(cls, timing: str):
        '''
        Takes an uninherited osu! timing and creates a single BpmOffset instance from it.
        Please read the osu! documentation for more info: [https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)#timing-points]
        ''' 
        timing_data = timing.split(',')

        return cls(
            offset = float(timing_data[0]),
            bpm = cls.to_bpm(float(timing_data[1])),
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
        beat_length = str(self.get_beat_length())
        meter = str(self.meter[0])
        
        return f'{time},{beat_length},{meter},{sample_set},{sample_index},{volume},0,0'