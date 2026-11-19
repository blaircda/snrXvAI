from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 

def call_example(model, sys_input, txt_input, max_output_tokens=20000):
    """
    For development purposes
    """


    if model["options"]["version"]=="good":
        output="\n\\begin{abstract}\nTest abstract, please ignore\n\\end{abstract}\n\\section{Introduction}Using the well-known Witten equation,\\begin{equation}E=mc^2\\end{equation} we find $\\alpha=2$.\n\\section{Conclusions}\nNone"
    elif model["options"]["version"]=="bad":
        output="\n\\begin{document}\\begin{abstract}\nTest abstract, please ignore\n\\end{abstract}\n\\section{Introduction}Using the well-known Witten equation,\\begin{equation}E=mc^2\\end{equation} we find $\\alpha=2$.\n\\section{Conclusions}\nNone\\end{document}"

    response = {
        "id": "12345",
        "status": "completed",
        "output": output,
        "thought_tokens": 0,
        "output_tokens": 0
    }

    return response

