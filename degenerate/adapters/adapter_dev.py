from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 

def call_example(model, sys_input, txt_input, max_output_tokens=20000):
    """
    For development purposes
    """


    if model["options"]["variant"]=="good":
        output="\n\\begin{abstract}\n We show that $E = mc^2$ and that $\mathrm{R}^k$ is empty.\n\\end{abstract}\n\\section{Introduction}Using the well-known Witten equation,\\begin{equation}E=mc^2\\end{equation} we find $\\alpha=2$.\n\\section{Conclusions}\nNone"
    elif model["options"]["variant"]=="bad_latex":
        output="\n\\begin{document}\\begin{abstract}\nTest abstract, please ignore\n\\end{abstract}\n\\section{Introduction}Using the well-known Witten equation,\\begin{equation}E=mc^2\\end{equation} we find $\\alpha=2$.\n\\section{Conclusions}\nNone\\end{document}"
    elif model["options"]["variant"]=="bad_markdown":
        output="Here is my draft of the paper:```LaTeX \n\\begin{abstract}\n We show that $x=4$ and so on.\n\\end{abstract}\n\\section{Introduction}Using the well-known Witten equation,\\begin{equation}E=mc^2\\end{equation} we find $\\alpha=2$.\n\\section{Conclusions}\nNone\n```"
    elif model["options"]["variant"]=="bad_compile":
        output="\n\\begin{abstract}\nThis model is good! Test abstract, please ignore\n\\end{abstract}\n\\section{Introduction}Using the well-known Witten equation,\\begin{equation}\E=mc^2\\end{equation} we find $\\alpha=2$.\n\\section{Conclusions}\nNone"

    response = {
        "id": "12345",
        "status": "completed",
        "output": output,
        "thought_tokens": 0,
        "output_tokens": 0
    }

    return response

