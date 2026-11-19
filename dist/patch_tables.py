import pathlib
import re

p = pathlib.Path("work/report-exp.tex")
tex = p.read_text()


def fix(m):
    return m.group(0).replace("\\texttt{", "\\breakabletexttt{")


tex = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", fix, tex, flags=re.S)
tex = re.sub(r"\\begin\{longtable\*\}.*?\\end\{longtable\*\}", fix, tex, flags=re.S)
p.write_text(tex)
