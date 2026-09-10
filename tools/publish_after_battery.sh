#!/bin/zsh
cd /Users/lindahoeberigs/claudecodedefault/nl-eval
S=${NLEVAL_LOG_DIR:-/tmp/nl-eval-logs}; mkdir -p $S
for i in $(seq 1 600); do grep -q "rob_local done" $S/rob_local.log 2>/dev/null && break; sleep 30; done
./.venv/bin/python -m nleval --publish results > /dev/null 2>&1; ./.venv/bin/python tools_readme_results.py > /dev/null 2>&1
pgrep -f "http.server 8765" >/dev/null || (./.venv/bin/python -m http.server 8765 --directory docs >/dev/null 2>&1 &); sleep 2
./.venv/bin/python tools_capture.py > $S/final-capture.log 2>&1
git add -A; git diff --cached --name-only | grep -iqE "key|secret|token|heldout/" && { echo "KEY FILE STAGED"; exit 1; }
git commit -q -m "Battery on the five local models" && git push -q origin HEAD 2>&1 | tail -1
echo "$(date +%H:%M) final_wait done"
