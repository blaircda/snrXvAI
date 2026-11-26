# snrXvAI

Bringing [snarXiv](https://snarxiv.org/) papers to artificial life as [snrXvAI](https://blaircda.github.io/snrXvAI/).

## Usage

**Preliminary: build the snarXiv grammar**

See [snarXiv on GitHub](https://github.com/davidsd/snarxiv) for the original.

In `degenerate/grammar`:

`perl compile-grammar snarxiv_titles.gram snarxiv_titles`

`ocamlc snarxiv_titles.ml -o title_generator`

**(For example) Generate 5 snarXiv paper titles, send these to AI models, with 1 paper being a collaboration between different models**

`python3 -m degenerate.main -N 5 -C 1`

Due to the potential to hit API errors, token limits and misguided LaTeX commands, it is possible that fewer than the specified number of papers are produced. 

The results of the run are saved to a new directory `output/`. Successfully created papers are logged as `output/listing.json` and the .tex and .pdf files are saved to `output/papers/`. Failures are logged as `output/errors.json` and explicit logs (and offending .tex files if available) are saved in `output/failed/`.

Other command line options:

| Option | Long form | Type | Default | Description |
|--------|-----------|------|---------|-------------|
| `-N` | `--Npapers` | int | 3 | Number of papers to generate |
| `-C` | `--Ncollabs` | int | 0 |Number of collaborative papers to generate|
| `-A` | `--max_paper_authors` | int | 2 | Maximum number of "authors" per paper |
| `-T` | `--single_title` | flag | off | Generate only one title, shared by all papers |
| `-M` | `--models` | choice | `balanced` | Model set to use: `all`, `dev`, `free`, `cheap`, or `balanced` |
| `-D` | `--max_dear_models` | int | 2 | Number of "expensive" models to use (only applies with `balanced` model choice) |
| `-S` | `--schedule` | flag | off | Apply scheduling logic, for remote automated runs. Cannot be used with other options |
| | `--run-ts` | custom timestamp YYYY-MM-DD_HHMMSS | set from time.gmtime() | Run timestamp string, can be set from command line for logging consistency |

Schedule sets `Npapers = 10`, `Ncollabs=3`, `max_paper_authors=2`, `models="balanced"`,  `max_dear_models=5`.
The schedule is set in the GitHub Actions workflow to currently run once a week.
Subject to change.

**Export the paper listing to HTML** 

`python3 -m degenerate.publish`

This creates `site/index.html` with associated `site/style.css` and `site/about.html`, with the pdf files in `site/pdf`.
It also copies over the results of a static experiment degenerating papers based on a snarXiv title AND abstract - these are the files in the directory `abs`.

**Publish the website using GitHub Pages**

Using a GitHub workflow, the resulting site is exported to [snrXvAI](https://blaircda.github.io/snrXvAI/)

## Acknowledgements

The snarXiv is of course the original and far more creative, correct and useful work of David Simmons-Duffin.
