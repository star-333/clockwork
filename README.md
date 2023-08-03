# clockwork
A small CLI for timing conversion between various music games. Only Stepmania, osu! and Soundodger 2 are supported at the moment but I am planning to cover more in the future.

## Installation
Clockwork can be installed with pip. To install, clone and move into the repository, and run the command:

```console
$ pip install .
```

Sorry, it's a little iffy right now. I'm still learning how to use setuptools... I will try to find a way to install it without having to clone the source code in the future.

## Usage
```console
$ clockwork "test/osu/Ariabl'eyeS - Arcadia (Hey lululu) [Lunar Eclipse].osu" -i osu -o stepmania --show-result

      i     | Successfully converted!
      i     | Tags copied to clipboard.
      i     | You can paste them directly into your .sm/.ssc, right at the end of the first section.
      i     | Be careful to remove the previous tags.

#OFFSET:3.72;
#BPMS:0.0=200.0
,734.5856=152.0
,737.5850666666666=152.0
,784.321=148.0
,785.293=144.0
,786.2498=138.0
,787.2046=132.0
,788.158=126.0
,789.11=120.0
,790.0766666666667=116.0
,791.0245=110.0
;
```

## Supported formats

| Format | Game         | Support | Notes                                                                                                            |
|--------|--------------|---------|------------------------------------------------------------------------------------------------------------------|
| `.osu` | osu!         | Yes     | Will implement volume, sample set and sample index of timing points in later versions                            |
| `.sm`  | Stepmania    | Partial | Stops not implemented yet                                                                                        |
| `.ssc` | Stepmania 5  | Partial | `.ssc` is built on top of `.sm` so timing points are the same                                                    |
| `.qua` | Quaver       | Yes     |                                                                                                                  |
| `.xml` | Soundodger 2 | Partial | Only conversion from Soundodger 2 is missing, due to timing information being stored in a different header file. |

## To-do list
- [ ] support for more file formats (.sm, .qua are on my watchlist. Feel free to suggest other formats!)
- [ ] direct injection of the timings into an already existing output file
