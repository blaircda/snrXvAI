import subprocess
from titlecase import titlecase
from pathlib import Path

def invariant_commands(word, **kwargs):
    if word and (word[0] in "$\\" or "\\" in word):
        return word
    return None


def generate_titles(N):
    DIR = Path(__file__).resolve().parent  # this file parent directory

    titles = []
    for N in range(N):
        proc = subprocess.run( DIR / "grammar"  / "title_generator", capture_output=True, text=True )
        titles.append( titlecase(proc.stdout.strip(), callback=invariant_commands) )

    return titles

if __name__ == "__main__":
    titles = generate_titles(2)
    #for t in titles:
    #    print(t)
