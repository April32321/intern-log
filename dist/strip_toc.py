import pathlib
import re

src = pathlib.Path("report.md").read_text()
start = src.index("## 目录")
end = src.index("---\n\n## 摘要")
body = src[:start] + src[end + 4:]
body = re.sub(r"\A# .*\n+", "", body, count=1)
pathlib.Path("work/report-export.md").write_text(body)
