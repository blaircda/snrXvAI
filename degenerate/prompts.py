SYS_PROMPT = """
Your job is to generate a fictitious hep-th article based on the given title. Keep it short - only 4-5 pages.

Your output will be inputted into a skeleton LaTeX file of the form
\documentclass[11pt]{article}
[PREAMBLE]
\begin{document}
\maketitle

YOUR OUTPUT GOES HERE

\end{document}

The [PREAMBLE] defines the following packages:
    xcolor (with dvipsnames), amssymb, amsfonts, amsmath, amsthm, cite, hyperref, tikz (with  libraries positioning, calc, arrows.meta)
Do not write any further packages into the file, and do not use \input, \include or \write to add content. 
Begin your output with an abstract enclosed by `\begin{abstract}` and `\end{abstract}`, followed by the body of the paper.
Use an inline bibliography enclosed by `\begin{thebibliography}` and `\end{thebibliography}'.
Output only LaTeX source and nothing else. Do not enclose the LaTeX source in any markdown.
"""

TITLE_LIST = [
    "The Solution of a Model for Spacetime Foam as Hyperplane Defects",
    "D-branes at the surface of the sun"
]
