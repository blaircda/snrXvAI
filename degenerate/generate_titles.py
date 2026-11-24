import subprocess
from titlecase import titlecase
from pathlib import Path
from degenerate.paths import GRAMMAR_DIR

def invariant_commands(word, **kwargs):
    if word and (word[0] in "$\\" or "\\" in word):
        return word
    return None

def generate_titles(N):
    if not check_grammar_exec():
        make_grammar_exec()       
    titles = []
    for N in range(N):
        proc = subprocess.run(str(GRAMMAR_DIR / "title_generator"), capture_output=True, text=True )
        titles.append( titlecase(proc.stdout.strip(), callback=invariant_commands) )
    return titles

def check_grammar_exec():
    """
    checks if the grammar executable is present
    and builds it if not
    """
    grammar_exec = GRAMMAR_DIR / "title_generator"
    if grammar_exec.is_file():
        return True
    else:
        return False            

def make_grammar_exec():
    """
    compiles grammar
    """
    grammar_defn = GRAMMAR_DIR / "snarxiv_titles.gram"
    compile_file = GRAMMAR_DIR / "compile-grammar"
    
    if not (grammar_defn.is_file() and compile_file.is_file()):
        raise SystemExit("Missing snarxiv_titles.gram or compile-grammar in degenerate/grammar")

    command_sequence = [
        ["perl", "compile-grammar", "snarxiv_titles.gram", "snarxiv.titles"],
        ["ocamlc", "snarxiv_titles.ml", "-o", "title_generator"],
    ]

    for command in command_sequence:
        try:
            subprocess.run(
                command, cwd=GRAMMAR_DIR, capture_output=True, text=True, check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"{' '.join(command)} failed with exit code {e.returncode}:\n{e.stderr}"
            ) from e

    for name in ("snarxiv_titles.cmi", "snarxiv_titles.cmo", "snarxiv_titles.ml"):
        (GRAMMAR_DIR / name).unlink(missing_ok=True)
    
if __name__ == "__main__": 
    titles = generate_titles(2)
    #for t in titles:
    #    print(t)
