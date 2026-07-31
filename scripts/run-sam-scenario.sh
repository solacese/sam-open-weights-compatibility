#!/usr/bin/env bash
# run-sam-scenario.sh — run a real SAM agent against your open-weights endpoint
# and check a validation scenario. This exercises the ACTUAL agent loop
# (streaming reassembly + multi-turn tool results), which the endpoint-only
# probe.sh cannot fully reproduce.
#
#   export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"
#   export SAM_TEST_API_BASE="http://localhost:8000/v1"
#   export SAM_TEST_API_KEY="sk-noop"
#   ./scripts/run-sam-scenario.sh [scenario]
#
# scenario defaults to two-tool-dependency; also: forced-tool, parallel-tools.
#
# Requires: `sam` on PATH (https://github.com/SolaceDev/solace-agent-mesh).
set -uo pipefail

: "${SAM_TEST_MODEL:?set SAM_TEST_MODEL}"
: "${SAM_TEST_API_BASE:?set SAM_TEST_API_BASE}"
export SAM_TEST_API_KEY="${SAM_TEST_API_KEY:-sk-noop}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCENARIO="${1:-two-tool-dependency}"
SCEN_FILE="$ROOT/tests/scenarios/$SCENARIO.yaml"
AGENT_CFG="$ROOT/tests/configs/agent.yaml"

[ -f "$SCEN_FILE" ] || { echo "no scenario '$SCENARIO' at $SCEN_FILE"; exit 2; }

if ! command -v sam >/dev/null 2>&1; then
  cat <<'EOF'
`sam` is not on PATH. This runner needs a SAM install to drive a live agent.

Without SAM you can still validate the hard gates against the raw endpoint:
    ./scripts/probe.sh

To install SAM: https://github.com/SolaceDev/solace-agent-mesh
EOF
  exit 2
fi

echo "== SAM scenario: $SCENARIO =="
echo "   model:    $SAM_TEST_MODEL"
echo "   endpoint: $SAM_TEST_API_BASE"
echo "   agent:    $AGENT_CFG"
echo

PROMPT=$(awk '/^prompt: \|/{f=1;next} f&&/^[a-z_]+:/{f=0} f{sub(/^  /,"");print}' "$SCEN_FILE")
echo "-- prompt --"; echo "$PROMPT"; echo

# Bring up SAM embedded with the validation agent, submit the prompt, capture the
# task trace, and assert on the observed tool calls. The exact invocation depends
# on your SAM version; the two common shapes:
#
#   A) sam run --embedded tests/configs/   then submit via the gateway/CLI
#   B) sam task run --agent ModelValidationAgent --config tests/configs/agent.yaml "$PROMPT"
#
# We try the task-run shape first (non-interactive, prints the trace), falling
# back to guidance if the subcommand differs on your build.

set -x
sam task run \
  --config "$AGENT_CFG" \
  --agent ModelValidationAgent \
  --format json \
  "$PROMPT" > /tmp/sam-validation-$SCENARIO.json 2> /tmp/sam-validation-$SCENARIO.log
RC=$?
set +x

if [ $RC -ne 0 ]; then
  echo
  echo "sam task run exited $RC. Your SAM build may use a different subcommand."
  echo "Inspect /tmp/sam-validation-$SCENARIO.log and adapt the invocation above."
  echo "Manual path: 'sam run --embedded tests/configs/' then submit the prompt via the UI/CLI,"
  echo "and check the task trace for the tool calls listed in $SCEN_FILE (assertions:)."
  exit $RC
fi

echo
echo "-- assertions (from $SCEN_FILE) --"
sed -n '/^assertions:/,/^pass_criteria:/p' "$SCEN_FILE"
echo
echo "Trace written to /tmp/sam-validation-$SCENARIO.json"
echo "Verify the tool calls + arguments in the trace match the assertions above."
echo "For two-tool-dependency the decisive check is: get_shipping_estimate was"
echo "called with warehouse=WH-DK-02 (the value lookup_order returned)."
