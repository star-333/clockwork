# MODULES
import click
import pyperclip
from sys import platform
from zenlog import log
# local
from timing import Timing

# FILE CONVERSION
class Convert:

    @staticmethod
    def osu_to_sd2(input_path: str, practice: bool = False):
        '''
        Takes in a .osu file and generates a soundodger 2 .xml file with the corresponding bookmarks in the same directory.
        - input_path: str | the path towards the .osu file

        OPTIONAL ARGS:
        - practice: bool | whether or not the bookmarks will be practice points

        Please read the osu! documentation for more info: [https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)]
        '''
        # format check
        if not input_path.endswith('.osu'):
            log.error('The input file format is not .osu')
            exit(1)
        
        # open file
        try:
            f = open(input_path, 'r', encoding='utf-8')
        except FileNotFoundError:
            log.error('File not found.')
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

        # convert to Timing instances
        for timing in osu_uninherited:
            bpm_list.append(Timing.from_osu(timing))

        # convert to sd2
        for bpm in bpm_list:
            sd2_bookmarks += bpm.to_sd2(practice) + '\n'

        # close .osu file
        f.close()

        # export to sd2 .xml file
        # to do later
        return sd2_bookmarks