SYS_PROMPT = r"""
You are a theoretical physicist writing a hep-th paper.
Your output will be inputted into a skeleton LaTeX file of the form
\documentclass[11pt]{article}
[PREAMBLE]
\begin{document}
\maketitle

YOUR OUTPUT GOES HERE

\end{document}

The [PREAMBLE] defines the following packages:
    xcolor (with dvipsnames), amssymb, amsfonts, amsmath, amsthm, cite, hyperref, tikz (with  libraries positioning, calc, arrows.meta)
Do not write any further packages into the file, and do not use \input, \include, \includegraphics, or \write to add content. 
Begin your output with an abstract enclosed by `\begin{abstract}` and `\end{abstract}`, followed by the body of the paper.
Use an inline bibliography enclosed by `\begin{thebibliography}` and `\end{thebibliography}'.
Output only LaTeX source and nothing else. Do not enclose the LaTeX source in any markdown.
"""

def make_user_prompt(stage, title, draft):
    if stage == "initial": # add more details later
        return f"Your job is to generate a fictitious hep-th article based on the following title: {title}. Keep it short - only 4-5 pages."
    elif stage == "revision": # add more details later
        return f"Your job is to revise a fictitious hep-th article, titled {title}. This title cannot be changed. Revise the draft: tighten the arguments, fix inconsistencies, keep the length and the format. The current draft of the paper is below.\n\nCURRENT DRAFT:\n{draft}"
    else:
        raise ValueError("Unknown prompt stage")

TITLE_LIST = [
    "The Solution of a Model for Spacetime Foam as Hyperplane Defects",
    "D-branes at the surface of the sun"
]
