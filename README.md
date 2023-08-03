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
$ clockwork "test/sm/STEP MACHINE.sm" -i stepmania -o osu --show-result

      i     | Successfully converted!
      i     | [TimingPoints] copied to clipboard.
      i     | You can paste it directly into your .osu, right after the [Events] section.
      i     | Be careful to remove the previous [TimingPoints] section.

[TimingPoints]
0,375.0,4,0,0,80,1,0
```

## Supported formats

| Format | Game         | Support | Notes                                                                                                            |
|--------|--------------|---------|------------------------------------------------------------------------------------------------------------------|
| `.osu` | osu!         | Yes     | Will implement volume, sample set and sample index of timing points later                                        |
| `.sm`  | Stepmania <5 | Partial | Stops not implemented yet. Conversion to Stepmania output is broken atm                                          |
| `.ssc` | Stepmania 5  | Partial | `.ssc` is built on top of `.sm` so timing points are the same                                                    |
| `.xml` | Soundodger 2 | Partial | Only conversion from Soundodger 2 is missing, due to timing information being stored in a different header file. |

## To-do list
- [ ] support for more file formats (.sm, .qua are on my watchlist. Feel free to suggest other formats!)
- [ ] direct injection of the timings into an already existing output file
