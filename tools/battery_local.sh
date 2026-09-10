#!/bin/zsh
cd /Users/lindahoeberigs/claudecodedefault/nl-eval
S=${NLEVAL_LOG_DIR:-/tmp/nl-eval-logs}; mkdir -p $S
for M in "qwen2.5:7b qwen2.5-7b" "gemma3:4b gemma3-4b" "llama3.2:3b llama3.2-3b" "phi4-mini phi4-mini" "hf.co/BramVanroy/GEITje-7B-ultra-GGUF:Q4_K_M geitje-7b-ultra"; do
  read -r model slug <<< "$M"
  echo "$(date +%H:%M) $slug start"
  ./.venv/bin/python -m nleval --robustness --suite core --limit 300 --workers 2 --provider ollama --model "$model" --out results/robustness__$slug.json > $S/rob-$slug.log 2>&1
  echo "$(date +%H:%M) $slug done: $(grep -E '"worst_case"' $S/rob-$slug.log | head -1)"
done
echo "$(date +%H:%M) rob_local done"
