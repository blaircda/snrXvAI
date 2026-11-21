# snrXvAI

Bringing [snarXiv](https://snarxiv.org/) papers to artificial life as [snrXvAI](https://blaircda.github.io/snrXvAI/)
## Usage

**Preliminary: build the snarXiv grammar**

See [snarXiv on GitHub](https://github.com/davidsd/snarxiv) for the original.

In `degenerate/grammar`:

`perl compile-grammar snarxiv_titles.gram snarxiv_titles`

`ocamlc snarxiv_titles.ml -o title_generator`

**Generate 5 snarXiv paper titles, send these to AI models, with 1 paper being a collaboration between different models**

`python3 -m degenerate.main -N 5 -C 1`

Due to the potential to hit API errors, token limits and misguided LaTeX commands, it is possible that fewer than the specified number of papers are produced. The successes are outputted to a new directory `papers/` and their details saved in `degenerate/listing.json`. The details of the failures are saved in `degenerate/errors.json`.

**Export the paper listing to HTML** 

`python3 -m degenerate.publish`

This creates `site/index.html` with associated `site/static/style.css` and `site/static/about.html`, with the pdf files in `site/pdf`

**Publish the website using GitHub Pages**

Using a GitHub workflow, the resulting site is exported to [snrXvAI](https://blaircda.github.io/snrXvAI/)
