import time, shutil, subprocess, tempfile, os, signal
from pathlib import Path
from degenerate.errors import GenerationError, OutputError


def make_paper(source):
    print(source)
    #filename = str(int(time.time()))+".tex" # choose better filename
    #with open("../dev/tex/"+filename,"w") as f:
    #    f.write(source)
    YYMM = time.strftime("%y%m", time.localtime())
    XXXXX = time.strftime("%w%m%S", time.localtime())[:5]
    papername = YYMM+"."+XXXXX
    paper_dir = Path("papers")
    paper_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        
        tex_env = {
        "PATH": os.environ["PATH"],   # so latexmk and pdflatex can be found
        "HOME": str(tmp),             
        "openin_any": "p",            # paranoid reading
        "openout_any": "p",           # paranoid writing
        }
        
        with open(tmp / f"{papername}.tex","w") as f:
            f.write(source)

        print("Building paper")
        cmd = ["latexmk", "-pdf",
               "-pdflatex=pdflatex -interaction=nonstopmode -no-shell-escape -halt-on-error %O %S",
               f"{papername}.tex"]

        proc = subprocess.Popen(cmd, cwd=tmp, env=tex_env,
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired as e:
            try:
                os.killpg(proc.pid, signal.SIGKILL)   # kill latexmk AND the pdflatex it started
            except ProcessLookupError:
                pass                                  # the group already ended by itself
            proc.communicate()                        # wait for it to end, close the pipes
            raise OutputError("Building pdf failed: timed out after 60s") from e

        if proc.returncode != 0:
            print(stdout)
            print(stderr)
            for f in [ f"{papername}.log"]:
                shutil.copy(tmp / f, paper_dir)
            raise OutputError(f"Building pdf failed (latexmk exit code {proc.returncode})")
        else:
            for f in [ f"{papername}.tex", f"{papername}.pdf"]:
                shutil.copy(tmp / f, paper_dir)

if __name__ == "__main__":
    source = """\\documentclass{article}
\\begin{document}
$E = mc^2$
\\end{document}"""
    make_paper(source)
