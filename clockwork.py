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
@click.argument('input', type = click.Path())
@click.option('--from', help = 'Convert from this file format.')
@click.option('--to', help = 'Convert to this file format.')
@click.option('--practice', is_flag = True, help = 'Make the bookmarks marked as practice points.')
@click.option('--show-result', is_flag = True, help = 'Show the results of the conversion on the terminal.')
@click.version_option()

def cli(input, practice, show_result):
    click.echo()

    output = Convert.to_sd2(Convert.from_osu(input))

    if show_result:
        click.echo()
        click.echo(output)



# MAIN
if __name__ == '__main__':
    cli()
