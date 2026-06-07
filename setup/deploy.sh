#!/bin/bash
# =============================================================================
# Perseus Memory Agent — Google Cloud Agent Builder Deployment
# =============================================================================
# Prerequisites:
#   1. gcloud CLI installed and authenticated: gcloud auth login
#   2. GCP project with billing enabled
#   3. Elastic Cloud account with Agent Builder enabled
#
# Usage:
#   export GCP_PROJECT_ID=your-project-id
#   export ELASTIC_MCP_ENDPOINT=https://your-deployment.es.us-central1.gcp.cloud.es.io:443
#   export ELASTIC_API_KEY=your-api-key
#   bash deploy.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info() { echo -e "${CYAN}[>]${NC} $1"; }

# ── Config ──────────────────────────────────────────────────────────────────
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
AGENT_NAME="${AGENT_NAME:-perseus-memory-agent}"
ELASTIC_MCP_ENDPOINT="${ELASTIC_MCP_ENDPOINT:-}"
ELASTIC_API_KEY="${ELASTIC_API_KEY:-}"

# ── Validation ──────────────────────────────────────────────────────────────
info "Checking prerequisites..."

command -v gcloud &>/dev/null || err "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
gcloud auth list --filter=status:ACTIVE --format='value(account)' | grep -q '@' || err "Not authenticated. Run: gcloud auth login"

if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    [ -n "$PROJECT_ID" ] || err "Set GCP_PROJECT_ID or run: gcloud config set project YOUR_PROJECT"
fi

log "Project: $PROJECT_ID"
log "Region: $REGION"

gcloud config set project "$PROJECT_ID" --quiet

# ── Enable APIs ─────────────────────────────────────────────────────────────
info "Enabling required APIs..."

gcloud services enable aiplatform.googleapis.com --project="$PROJECT_ID" --quiet 2>/dev/null || true
gcloud services enable discoveryengine.googleapis.com --project="$PROJECT_ID" --quiet 2>/dev/null || true

log "APIs enabled (Vertex AI + Discovery Engine)"

# ── Check existing agent ────────────────────────────────────────────────────
info "Checking for existing agent '$AGENT_NAME'..."

EXISTING_AGENT=$(gcloud alpha ai agents list \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --filter="displayName:$AGENT_NAME" \
    --format='value(name)' 2>/dev/null || echo "")

if [ -n "$EXISTING_AGENT" ]; then
    warn "Agent '$AGENT_NAME' already exists: $EXISTING_AGENT"
    AGENT_ID="$EXISTING_AGENT"
else
    # ── Create Agent ─────────────────────────────────────────────────────────
    info "Creating agent '$AGENT_NAME'..."

    # Agent Builder uses the discoveryengine API for agent creation
    # The agent is a "chat app" engine with Gemini as the model
    AGENT_CONFIG=$(cat <<EOF
{
  "displayName": "$AGENT_NAME",
  "dataStoreIds": [],
  "solutionType": "SOLUTION_TYPE_CHAT",
  "industryVertical": "GENERIC",
  "searchEngineConfig": {
    "searchTier": "SEARCH_TIER_ENTERPRISE",
    "searchAddOns": ["SEARCH_ADD_ON_LLM"]
  },
  "chatEngineConfig": {
    "agentCreationConfig": {
      "business": "Perseus Memory Agent",
      "defaultLanguageCode": "en",
      "timeZone": "America/Chicago",
      "location": "global"
    }
  }
}
EOF
)

    # Create via Vertex AI Agent Builder REST API
    CREATE_RESPONSE=$(curl -s -X POST \
        "https://discoveryengine.googleapis.com/v1/projects/$PROJECT_ID/locations/global/collections/default_collection/engines" \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -d "$AGENT_CONFIG" 2>/dev/null || echo "")

    if echo "$CREATE_RESPONSE" | grep -q '"name"'; then
        AGENT_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])" 2>/dev/null)
        log "Agent created: $AGENT_ID"
    else
        warn "REST API agent creation returned: $CREATE_RESPONSE"
        warn "Agent Builder may require console-based creation for first agent."
        warn "Open: https://console.cloud.google.com/gen-app-builder/agents?project=$PROJECT_ID"
        warn "Create agent named '$AGENT_NAME' with Gemini model, then re-run this script with AGENT_ID set."
        exit 1
    fi
fi

# ── Get Agent Endpoint ──────────────────────────────────────────────────────
info "Getting agent details..."

AGENT_DETAILS=$(curl -s \
    "https://discoveryengine.googleapis.com/v1/$AGENT_ID" \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" 2>/dev/null)

# ── Display Results ─────────────────────────────────────────────────────────
echo ""
echo "=============================================="
echo "  Perseus Memory Agent — Deployment Summary"
echo "=============================================="
echo ""
echo "  Agent ID:   $AGENT_ID"
echo "  Region:     $REGION"
echo ""
echo "  Chat URL:   https://console.cloud.google.com/gen-app-builder/agents/$AGENT_ID/chat?project=$PROJECT_ID"
echo ""
echo "  Add this to your .env:"
echo "  GCP_PROJECT_ID=$PROJECT_ID"
echo "  GCP_REGION=$REGION"
echo ""
echo "=============================================="
echo ""

# ── Elastic MCP Connection ──────────────────────────────────────────────────
if [ -n "$ELASTIC_MCP_ENDPOINT" ]; then
    info "Configuring Elastic MCP connection..."
    warn "MCP server connection is configured in Agent Builder Console."
    info "Open: https://console.cloud.google.com/gen-app-builder/agents?project=$PROJECT_ID"
    info "Select '$AGENT_NAME' → Tools → Add MCP Server"
    info "Endpoint: $ELASTIC_MCP_ENDPOINT"
    info "Auth: API Key"
fi

# ── Next Steps ──────────────────────────────────────────────────────────────
echo ""
echo "Next steps:"
echo "  1. Open Agent Builder Console (link above)"
echo "  2. Go to Tools → Add MCP Server → paste your Elastic endpoint"
echo "  3. Define MCP tools: search_memory, store_memory, delete_memory"
echo "  4. Test the agent in the chat playground"
echo "  5. Use the chat URL as your 'Hosted Project URL' in Devpost"
echo ""
log "Deployment script complete."
