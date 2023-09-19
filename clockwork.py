# clockwork v0.3.0

# MODULES
import click
import pyperclip
from sys import platform
from zenlog import log
# local
from timing import Timing
from convert import Convert



# CLI
@click.command()
@click.version_option()
@click.argument('input', 
    type = click.Path()
)

# io
@click.option('--in-format', '-i',
    type = click.Choice(['osu', 'stepmania', 'quaver'], case_sensitive = False),
    required = True,
    help = 'The format to convert timings from.',
)
@click.option('--out-format', '-o',
    type = click.Choice(['osu', 'sd2', 'stepmania', 'quaver'], case_sensitive = False),
    required = True,
    help = 'The format to convert timings to.',
)
@click.option('--show-result', '-s',
    is_flag = True, 
    help = 'Show the results of the conversion on the terminal.'
)

# sd2
@click.option('--practice/--no-practice',
    is_flag = True,
    help = 'If -o is sd2, turn the bookmarks into practice points (or not). Ignored if --out-format is not sd2.'
)

# osu
@click.option('--sample-set',
    type = click.IntRange(0, 3, clamp=True),
    required = False,
    default = 0,
    help = 'If -o is osu, use the provided sample_set value in timing points.'
)
@click.option('--sample-index',
    type = int,
    default = 0,
    required = False,
    help = 'If -o is osu, use the provided sample_index value in timing points.'
)
@click.option('--volume',
    type = click.IntRange(0, 100),
    default = 80,
    required = False,
    help = 'If -o is osu, use the provided volume value in timing points.'
)

# cli command
def cli(input, in_format, out_format, show_result, practice, volume, sample_set, sample_index):

    click.echo()

    # FIRST PASS: convert to Timing instances
    if in_format == 'osu':
        first_pass = Convert.from_osu(input)

    elif in_format == 'stepmania': 
        first_pass = Convert.from_stepmania(input)

    elif in_format == 'quaver': 
        first_pass = Convert.from_quaver(input)


    # SECOND PASS: convert to file snippets
    if out_format == 'osu':
        second_pass = Convert.to_osu(first_pass, volume, sample_set, sample_index) # implement volume, sample_set, sample_index later

    elif out_format == 'stepmania':
        second_pass = Convert.to_stepmania(first_pass)

    elif out_format == 'sd2':
        if practice: 
            second_pass = Convert.to_sd2(first_pass, practice = True)
        else: 
            second_pass = Convert.to_sd2(first_pass)

    elif out_format == 'quaver':
        second_pass = Convert.to_quaver(first_pass)
        

    if show_result:
        click.echo()
        click.echo(second_pass)



# MAIN
if __name__ == '__main__':
    cli()