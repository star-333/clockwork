# clockwork
A small python program for timing conversion from osu! to Soundodger 2. I originally made this with only my own use in mind; thus, this tool only covers osu! to Soundodger 2 conversion, but I am planning to cover more music games in the future.

## Requirements
Clockwork requires a few things to run:
- [python v3.11 or higher](https://www.python.org/)
- [click v8.1 or higher](https://click.palletsprojects.com/en/8.1.x/)
- [pyperclip](https://pypi.org/project/pyperclip/)

[zenlog](https://github.com/ManufacturaInd/python-zenlog) is recommended but not required; if not installed, the log messages will just be uglier.
All of the aforementionned  packages can easily be installed with pip.

## Usage
```
$ python clockwork.py "Ariabl'eyeS - Arcadia (Hey lululu) [Lunar Eclipse].osu" --show
      i     | Successfully converted!

<Bookmark time="3.72" col="FFFFFF" label="3.72 / 200.0" />
<Bookmark time="293.688" col="FFFFFF" label="293.688 / 152.0" />
<Bookmark time="294.872" col="FFFFFF" label="294.872 / 152.0" />
<Bookmark time="313.819" col="FFFFFF" label="313.819 / 148.0" />
<Bookmark time="314.224" col="FFFFFF" label="314.224 / 144.0" />
<Bookmark time="314.64" col="FFFFFF" label="314.64 / 138.0" />
<Bookmark time="315.074" col="FFFFFF" label="315.074 / 132.0" />
<Bookmark time="315.528" col="FFFFFF" label="315.528 / 126.0" />
<Bookmark time="316.004" col="FFFFFF" label="316.004 / 120.0" />
<Bookmark time="316.504" col="FFFFFF" label="316.504 / 116.0" />
<Bookmark time="317.021" col="FFFFFF" label="317.021 / 110.0" />

      i     | Bookmarks copied to clipboard. You can paste them directly into your .xml, right after the <Editor ... /> element.
```

# To-do list
- [ ] support for more file formats (.sm, .qua are on my watchlist. Feel free to suggest other formats!)
- [ ] direct injection of the timings into an already existing output file
