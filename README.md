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

Due to the potential to hit API errors, token limits and misguided LaTeX commands, it is possible that fewer than the specified number of papers are produced. The successes are outputted to a new directory `papers/` and their details saved in `degenerate/listing.json`. The details of the failures are saved as `failed/errors.json` along with the offending .tex and .log files if available.

Other command line options (default of "none ($k$)" means the value $k$ is set internally):

| Option | Long form | Type | Default | Description |
|--------|-----------|------|---------|-------------|
| `-N` | `--Npapers` | int | none (3) | Number of papers to generate |
| `-C` | `--Ncollabs` | int | none (0) | Number of collaborative papers to generate|
| `-A` | `--max_paper_authors` | int | none (2) | Maximum number of "authors" per paper |
| `-T` | `--single_title` | flag | off | Generate only one title, shared by all papers |
| `-M` | `--models` | choice | none (2) | Model set to use: `all`, `dev`, `free` or `budget` |
| `-P` | `--paid` | int | none | Number of paid models to use (with `budget` model choice) |
| `-S` | `--schedule` | flag | off | Apply scheduling logic, for remote automated runs. Cannot be used with other options |

**Export the paper listing to HTML** 

`python3 -m degenerate.publish`

This creates `site/index.html` with associated `site/style.css` and `site/about.html`, with the pdf files in `site/pdf`.
The export also publishes the results of an experiment using snarXiv title AND abstract to the website - these are the files in the directory `abs`.

**Publish the website using GitHub Pages**

Using a GitHub workflow, the resulting site is exported to [snrXvAI](https://blaircda.github.io/snrXvAI/)
