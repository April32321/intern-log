#!/usr/bin/env bash
set -euo pipefail

fail=0
need_gb=150

check() { printf '%-24s %s\n' "$1" "$2"; }

# 1) 系统
if [ "$(uname -s)" = "Darwin" ]; then
  os_name="$(sw_vers -productName) $(sw_vers -productVersion)"
elif [ -r /etc/os-release ]; then
  os_name="$(. /etc/os-release && printf '%s' "${PRETTY_NAME:-unknown}")"
else
  os_name="unknown"
fi
check "OS" "$os_name"
check "Arch" "$(uname -m)"

# 2) CPU 核数
if command -v nproc >/dev/null 2>&1; then
  cores="$(nproc)"
else
  cores="$(sysctl -n hw.ncpu 2>/dev/null || echo unknown)"
fi
check "CPU cores" "$cores"

# 3) 家目录可用空间（GB）
avail=""
if avail="$(df -BG --output=avail "$HOME" 2>/dev/null | tail -n 1 | tr -dc '0-9')" && [ -n "$avail" ]; then
  :
else
  avail="$(df -g "$HOME" | awk 'NR==2 {print $4}')"
fi
check "Home avail(GB)" "${avail:-unknown}"

if [ -n "$avail" ] && [ "$avail" -lt "$need_gb" ]; then
  echo "WARN: 空间不足 ${need_gb}GB"
  fail=1
fi

# 4) 命令是否存在
for c in git curl tar wget python3 conda docker; do
  if p="$(command -v "$c")"; then
    check "$c" "$p"
  else
    check "$c" "MISSING"
  fi
done
check "kilo" "$(command -v kilo || echo MISSING)"

# 5) 结论
echo "----"
if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS"
  exit 0
else
  echo "RESULT: WARN"
  exit 1
fi
