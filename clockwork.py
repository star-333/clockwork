# clockwork v0.1
# requires python 3.6 or higher, click, pyperclip. zenlog is recommended but not required
# i should probably check [https://github.com/SaxxonPike/rhythm-game-formats/tree/master] too

# MODULES
try:
    from zenlog import log as logging
except ModuleNotFoundError:
    import logging
    logging.getLogger().setLevel(logging.INFO)

import click
import pyperclip
from sys import platform

# CONSTANTS
SD2_COLOR = 'FFFFFF'





# BPMOFFSET CLASS / TIMING FUNCTIONS
class BpmOffset:
    '''
    An offset / BPM / meter group. The offset is in milliseconds.
    - self.offset: float
    - self.bpm: float
    - self.meter: tuple[int, int]
    '''

    def __init__(self, offset: float, bpm: float, meter: tuple[int, int] = (4,4)):
        self.offset = offset
        self.bpm = bpm
        self.meter = meter


    def __repr__(self):
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


    def to_sd2(self, practice: bool = False) -> str:
        '''
        Returns a string containing a soundodger bookmark with offset and BPM in its title.

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

    
    @classmethod
    def from_osu(cls, timing: str):
        '''
        Takes an uninherited osu! timing and creates a BpmOffset instance from it.
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
        Returns a string containing an uninherited osu timing.

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



# FILE CONVERSION
def convert_osu_to_sd2(input_path: str, practice: bool = False):
    '''
    Takes in a .osu file and generates a soundodger 2 .xml file with the corresponding bookmarks in the same directory.
    - input_path: str | the path towards the .osu file

    OPTIONAL ARGS:
    - practice: bool | whether or not the bookmarks will be practice points

    Please read the osu! documentation for more info: [https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)]
    '''

    # format check
    if not input_path.endswith('.osu'):
        logging.error('The input file format is not .osu')
        exit(1)
    
    # open file
    try:
        f = open(input_path, 'r', encoding='utf-8')
    except FileNotFoundError:
        logging.error('File not found.')
        exit(1)

    osu_content = f.read().split('\n\n')
    osu_timing_points = []
    osu_uninherited = []
    bpm_list = []
    sd2_bookmarks = ''

    # extract [TimingPoints]
    for section in osu_content:
        if section.startswith('[TimingPoints]'):
            osu_timing_points = section.split('\n')[1:]
            break
    
    # extract uninherited
    for timing in osu_timing_points:
        # check uninherited flag
        if timing.split(',')[-2] == '1': 
            osu_uninherited.append(timing)

    # convert to BpmOffset
    for timing in osu_uninherited:
        bpm_list.append(BpmOffset.from_osu(timing))

    # convert to sd2
    for bpm in bpm_list:
        sd2_bookmarks += bpm.to_sd2(practice) + '\n'

    # close .osu file
    f.close()

    # export to sd2 .xml file
    # to do later
    return sd2_bookmarks



# CLI
@click.command()
@click.argument('input', type = click.Path())
@click.option('--practice', is_flag = True, help = 'Make the bookmarks marked as practice points.')
@click.option('--show-result', is_flag = True, help = 'Show the results of the conversion on the terminal.')
def cli(input, practice, show_result):

    output = convert_osu_to_sd2(input, practice)
    logging.info('Successfully converted!')

    if show_result:
        click.echo()
        click.echo(output)

    pyperclip.copy(output)
    logging.info('Bookmarks copied to clipboard. You can paste them directly into your .xml, right after the <Editor ... /> element.')



# MAIN
if __name__ == '__main__':
    cli()
