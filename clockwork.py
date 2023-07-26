# clockwork v0.1
# requires python 3.6 or higher, click, pyperclip. zenlog is recommended but not required
# i should probably check [https://github.com/SaxxonPike/rhythm-game-formats/tree/master] too

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
    type = click.Choice(['osu', 'stepmania'], case_sensitive = False),
    required = True,
    help = 'The format to convert timings from.',
)
@click.option('--out-format', '-o',
    type = click.Choice(['osu', 'sd2', 'stepmania'], case_sensitive = False),
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
    prompt = 'Make the bookmarks into practice points?'
)

# cli command
def cli(input, in_format, out_format, show_result, practice):

    click.echo()

    # FIRST PASS: convert to Timing instances
    if in_format == 'osu': 
        first_pass = Convert.from_osu(input)

    elif in_format == 'stepmania': 
        first_pass = Convert.from_stepmania(input)


    # SECOND PASS: convert to file snippets
    if out_format == 'osu': 
        second_pass = Convert.to_osu(first_pass) # implement volume, sample_set, sample_index later

    elif out_format == 'stepmania':
        second_pass = Convert.to_stepmania(first_pass)

    elif out_format == 'sd2':
        if practice: second_pass = Convert.to_sd2(first_pass, practice = True)
        else: second_pass = Convert.to_sd2(first_pass)
        

    if show_result:
        click.echo()
        click.echo(second_pass)



# MAIN
if __name__ == '__main__':
    cli()
