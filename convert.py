# MODULES
import click
import pyperclip
from sys import platform
from zenlog import log
import re
# local
from timing import Timing, TimingList



# UTILS
def check_format(input_path: str, ext: str | tuple[str, ...]):
    '''
    Checks the extension of a file. Return True and proceed if the extension matches, exit otherwise.
    
    - input_path: str | the path towards the file
    - ext: str | tuple[str, ...] | the extension(s)
    '''
    
    if isinstance(ext, str):
        if not input_path.endswith(f'.{ext}'):
            log.error(f'The input file format is not .{ext}')
            exit(1)

        return True

    else:
        for x in ext:
            if input_path.endswith(f'.{x}'):
                return True
        
        log.error(f'The input file format is not .{x}')
        exit(1)

        


def open_file(input_path: str, mode: str = 'r'):
    '''
    Tries to open a file. Return the file object and proceed if succeeded, exit otherwise.

    - input_path: str | the path towards the file
    - mode: str | mode in which the file is opened
    '''
    try:
        f = open(input_path, mode, encoding='utf-8')
        return f
    
    except FileNotFoundError:
        log.error('File not found.')
        exit(1)



# FILE CONVERSION
class Convert:

    ### OSU ###

    @staticmethod
    def from_osu(input_path: str) -> list[Timing]:
        '''
        Takes in a .osu file and generates a list of Timing points accordingly.

        - input_path: str | the path towards the .osu file

        Please read the osu! documentation for more info: [https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)]
        '''
        check_format(input_path, 'osu')
        f = open_file(input_path)

        osu_content = f.read().split('\n\n')
        osu_timing_points = []
        osu_uninherited = []
        timing_list = []

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
            timing_list.append(Timing.from_osu(timing))

        f.close()
        return timing_list


    @staticmethod
    def to_osu(timings: list[Timing], volume: int = 80, sample_set: int=0, sample_index: int=0) -> str:
        '''
        Takes a list of Timing instances and generates a .osu snippet with the corresponding bookmarks.

        - timings: list[Timings] | a list of Timing instances
        '''
        res = '[TimingPoints]\n'

        # normalize
        if volume >= 100: volume_n = 100
        else: volume_n = volume

        for t in timings:
            res += t.to_osu(volume, sample_set, sample_index) + '\n'

        log.info('Successfully converted!')

        pyperclip.copy(res)
        log.info('[TimingPoints] copied to clipboard.\nYou can paste it directly into your .osu, right after the [Events] section.\nBe careful to remove the previous [TimingPoints] section.')

        return res


    ### SOUNDODGER 2 ###

    @staticmethod
    def to_sd2(timings: list[Timing], practice: bool = False) -> str:
        '''
        Takes in a list of Timing instances and generates a soundodger 2 .xml snippet with the corresponding bookmarks.

        - timings: list[Timings] | a list of Timing instances

        OPTIONAL ARGS:
        - practice: bool | whether or not the bookmarks will be practice points
        '''
        res = ''

        for t in timings:
            res += t.to_sd2(practice) + '\n'

        log.info('Successfully converted!')
        
        pyperclip.copy(res)
        log.info('Bookmarks copied to clipboard.\nYou can paste them directly into your .xml, right after the <Editor ... /> element.')

        return res

    
    ### STEPMANIA ###

    @staticmethod
    def from_stepmania(input_path: str) -> list[Timing]:
        '''
        Takes in a .sm or .ssc file and generates a list of Timing points accordingly.
        Works with .sm and .ssc formats.
        NOTE: Only #BPMS is supported at the moment. #STOPS will be implemented in the future.

        - input_path: str | the path towards the .sm/.ssc file

        Please read the Stepmania documentation for more info: 
        [https://github.com/stepmania/stepmania/wiki/sm]
        [https://github.com/stepmania/stepmania/wiki/ssc]
        '''
        check_format(input_path, ('sm', 'ssc'))
        f = open_file(input_path)

        sm_content = f.read()
        
        # offset
        try:
            offset_rawstr = re.findall('#OFFSET:.*;', sm_content)[0]        # extract raw tag
            offset_split = re.split('[,;:]', offset_rawstr)                 # split tag
            offset = [x for x in offset_split if x][1]                      # extract relevant items
        except:
            offset = '0.000000'

        #bpm
        bpm_rawstr = re.findall('#BPMS:[^;]*;', sm_content, re.DOTALL)[0]   # extract raw tag
        bpm_split = re.split('[,;:\s]', bpm_rawstr)                         # split tag
        bpm = [x for x in bpm_split if x][1:]                               # extract relevant items
        
        f.close()
        return TimingList.from_stepmania(float(offset), bpm)
    

    @staticmethod
    def to_stepmania(timings: list[Timing]) -> str:
        '''
        Takes a list of Timing instances and generates a .sm/.ssc snippet with the corresponding bookmarks.

        - timings: list[Timings] | a list of Timing instances
        '''
        content = TimingList.to_stepmania(timings)
        res = f'{content[1]}\n{content[0]}'
        
        log.info('Successfully converted!')
        
        pyperclip.copy(res)
        log.info('Tags copied to clipboard.\nYou can paste them directly into your .sm/.ssc, right at the end of the first section.\nBe careful to remove the previous tags.')

        return res

    
    ### QUAVER ###
    @staticmethod
    def from_quaver(input_path: str) -> list[Timing]:
        '''
        Takes a .qua file and returns a list of Timings accordingly.

        - input_path: str | the path towards the .sm/.ssc file

        Please read the Quaver API source code for more info:
        [https://github.com/Quaver/Quaver.API/blob/master/Quaver.API/Maps/Qua.cs]
        '''
        check_format(input_path, 'qua')
        f = open_file(input_path)

        qua_content = f.read()

        timings_rawstr = re.findall('TimingPoints.*SliderVelocities', qua_content, re.DOTALL)[0]        # extract raw string
        timings_rawstr = re.sub('TimingPoints:\n', '', timings_rawstr)                                  # remove unnecessary info
        timings_rawstr = re.sub('SliderVelocities', '', timings_rawstr)                                 # remove unnecessary info
        timings_split = timings_rawstr.split('- ')[1:]
        
        f.close()
        return [Timing.from_quaver(t) for t in timings_split]



if __name__ == '__main__':
    print(Convert.from_quaver('test/qua/14509.qua'))