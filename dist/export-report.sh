#!/usr/bin/env bash
# 导出 report.md → dist/report.html（单文件，图片内嵌）与 dist/report.pdf（xelatex + 宋体）
# 用法：./dist/export-report.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist work

HDR=work/export-header.tex
cat > "$HDR" <<'TEX'
\usepackage{amssymb}
\usepackage{etoolbox}
\usepackage{newunicodechar}
\newunicodechar{⊂}{\ensuremath{\subset}}
\newunicodechar{✓}{\ensuremath{\checkmark}}
\newunicodechar{⁰}{\textsuperscript{0}}
\newunicodechar{¹}{\textsuperscript{1}}
\newunicodechar{²}{\textsuperscript{2}}
\newunicodechar{³}{\textsuperscript{3}}
\newunicodechar{⁴}{\textsuperscript{4}}
\newunicodechar{⁵}{\textsuperscript{5}}
\newunicodechar{⁶}{\textsuperscript{6}}
\newunicodechar{⁷}{\textsuperscript{7}}
\newunicodechar{⁸}{\textsuperscript{8}}
\newunicodechar{⁹}{\textsuperscript{9}}
\xeCJKDeclareCharClass{CJK}{"2460 -> "2473}
\setlength{\tabcolsep}{2pt}
\setlength{\emergencystretch}{3em}
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{Shaded}{\footnotesize}
\usepackage{seqsplit}
\newcommand{\breakabletexttt}[1]{\texttt{\seqsplit{#1}}}
\usepackage{fvextra}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
TEX

# 1) HTML：自包含（图片与 CSS 内嵌）
pandoc report.md -o dist/report.html --standalone --embed-resources \
  --css=dist/report.css \
  --metadata title="基于公开 CT 影像组学的 NSCLC 生存分析复现：实习报告"

# 2) PDF：去掉手写目录（改用 LaTeX 目录），标题移到文档元数据
python3 dist/strip_toc.py

pandoc work/report-export.md -o work/report-exp.tex --standalone --toc --toc-depth=2 \
  -H "$HDR" -V toc-title="目录" \
  -V CJKmainfont="Songti SC" -V mainfont="Times New Roman" -V monofont="Menlo" \
  -V fontsize=10pt -V geometry:"margin=2cm" -V linestretch=1.15 \
  -V colorlinks=true -V linkcolor=blue -V urlcolor=blue \
  --metadata title="基于公开 CT 影像组学的 NSCLC 生存分析复现：实习报告"

# 3) 表格单元格里的长路径允许断行（seqsplit 不能用于标题/目录这类移动参数）
python3 dist/patch_tables.py

# 两遍：第一遍写 .toc，第二遍才有目录页码
rm -f work/report-exp.aux work/report-exp.toc work/report-exp.out work/report-exp.log
xelatex -interaction=nonstopmode -output-directory=work work/report-exp.tex >/dev/null
xelatex -interaction=nonstopmode -output-directory=work work/report-exp.tex >/dev/null
cp work/report-exp.pdf dist/report.pdf
echo "errors: $(grep -c '^! ' work/report-exp.log || true)  overfull: $(grep -c 'Overfull \\hbox' work/report-exp.log || true)"
ls -lh dist/report.pdf dist/report.html
