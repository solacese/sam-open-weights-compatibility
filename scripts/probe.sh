#!/usr/bin/env bash
# probe.sh — check the three SAM hard gates directly against an OpenAI-compatible
# endpoint. No SAM required. Uses curl + jq only.
#
#   export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"  # provider/model
#   export SAM_TEST_API_BASE="http://localhost:8000/v1"
#   export SAM_TEST_API_KEY="sk-noop"
#   ./scripts/probe.sh
#
# The model string is sent to the endpoint WITHOUT the provider prefix
# (the prefix is a SAM/LiteLLM concept; the raw endpoint wants the bare name).
set -uo pipefail

: "${SAM_TEST_MODEL:?set SAM_TEST_MODEL, e.g. openai/Qwen/Qwen2.5-32B-Instruct}"
: "${SAM_TEST_API_BASE:?set SAM_TEST_API_BASE, e.g. http://localhost:8000/v1}"
API_KEY="${SAM_TEST_API_KEY:-sk-noop}"

# Strip a leading provider prefix (openai/, ollama/, cohere/, ...) for the raw call.
BARE_MODEL="${SAM_TEST_MODEL#*/}"
URL="${SAM_TEST_API_BASE%/}/chat/completions"

command -v jq >/dev/null || { echo "jq is required"; exit 2; }

pass=0; fail=0
green() { printf '\033[32m%s\033[0m\n' "$1"; }
red()   { printf '\033[31m%s\033[0m\n' "$1"; }

TOOLS='[{"type":"function","function":{"name":"get_weather","description":"Get current weather for a city","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}]'

echo "== Probing $BARE_MODEL at $URL =="
echo

# ---- H1: native tool call (non-streaming) --------------------------------
echo "[H1] native tool call ..."
REQ1=$(jq -n --arg m "$BARE_MODEL" --argjson tools "$TOOLS" \
  '{model:$m, tools:$tools, tool_choice:"auto", messages:[{role:"user",content:"What is the weather in Copenhagen right now?"}]}')
RESP1=$(curl -sS -X POST "$URL" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d "$REQ1")
NAME1=$(echo "$RESP1" | jq -r '.choices[0].message.tool_calls[0].function.name // empty' 2>/dev/null)
ARGS1=$(echo "$RESP1" | jq -r '.choices[0].message.tool_calls[0].function.arguments // empty' 2>/dev/null)
CALL_ID=$(echo "$RESP1" | jq -r '.choices[0].message.tool_calls[0].id // "call_1"' 2>/dev/null)
if [ "$NAME1" = "get_weather" ] && echo "$ARGS1" | jq -e '.city' >/dev/null 2>&1; then
  green "  PASS — tool_calls[0]=get_weather args=$ARGS1"; pass=$((pass+1))
else
  red   "  FAIL — no valid get_weather tool call. raw: $(echo "$RESP1" | head -c 400)"; fail=$((fail+1))
fi
echo

# ---- H2: streaming tool call --------------------------------------------
echo "[H2] streaming tool call ..."
REQ2=$(echo "$REQ1" | jq '. + {stream:true}')
STREAM=$(curl -sS -N -X POST "$URL" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d "$REQ2")
# Concatenate streamed argument fragments across SSE chunks.
FRAG=$(echo "$STREAM" | sed -n 's/^data: //p' | grep -v '^\[DONE\]' \
  | jq -rj '.choices[0].delta.tool_calls[0].function.arguments // empty' 2>/dev/null)
SAW_NAME=$(echo "$STREAM" | sed -n 's/^data: //p' | grep -v '^\[DONE\]' \
  | jq -r '.choices[0].delta.tool_calls[0].function.name // empty' 2>/dev/null | grep -m1 . || true)
if [ "$SAW_NAME" = "get_weather" ] && echo "$FRAG" | jq -e '.city' >/dev/null 2>&1; then
  green "  PASS — streamed tool call reassembled: $FRAG"; pass=$((pass+1))
else
  red   "  FAIL — streamed deltas did not reassemble into a valid tool call."
  red   "         name=$SAW_NAME frag=$FRAG (server may not emit tool-call deltas while streaming)"; fail=$((fail+1))
fi
echo

# ---- H3: tool-result turn ------------------------------------------------
echo "[H3] tool-result turn ..."
REQ3=$(jq -n --arg m "$BARE_MODEL" --arg cid "$CALL_ID" --arg args "${ARGS1:-{\"city\":\"Copenhagen\"}}" \
  '{model:$m, messages:[
     {role:"user",content:"What is the weather in Copenhagen right now?"},
     {role:"assistant",content:null,tool_calls:[{id:$cid,type:"function",function:{name:"get_weather",arguments:$args}}]},
     {role:"tool",tool_call_id:$cid,content:"{\"city\":\"Copenhagen\",\"temp_c\":18,\"conditions\":\"partly cloudy\"}"}
   ]}')
RESP3=$(curl -sS -X POST "$URL" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d "$REQ3")
FINAL=$(echo "$RESP3" | jq -r '.choices[0].message.content // empty' 2>/dev/null)
RECALLED=$(echo "$RESP3" | jq -r '.choices[0].message.tool_calls[0].function.name // empty' 2>/dev/null)
if echo "$FINAL" | grep -Eiq '18|partly cloudy' && [ -z "$RECALLED" ]; then
  green "  PASS — used the tool result: $(echo "$FINAL" | head -c 200)"; pass=$((pass+1))
else
  red   "  FAIL — did not use the tool result (recalled=$RECALLED). answer: $(echo "$FINAL" | head -c 200)"; fail=$((fail+1))
fi
echo

echo "== Result: $pass passed, $fail failed =="
if [ "$fail" -eq 0 ]; then
  green "All hard gates PASS — proceed to run-sam-scenario.sh for the full agent-loop test."
  exit 0
else
  red "One or more hard gates FAILED — see docs/validation.md ('Reading failures'). NOT SAM-compatible on this stack yet."
  exit 1
fi
