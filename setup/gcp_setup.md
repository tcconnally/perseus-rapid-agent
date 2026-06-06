# Google Cloud Setup Guide

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable billing (required for Vertex AI)

## 2. Enable Required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  cloudresourcemanager.googleapis.com
```

Or enable via Console → APIs & Services → Library:
- **Vertex AI API**
- **Cloud Resource Manager API**

## 3. Set Up Vertex AI Agent Builder

1. Go to [Vertex AI Agent Builder](https://console.cloud.google.com/gen-app-builder/agents)
2. Click "Create Agent"
3. Select **Gemini 3 Pro** as the model
4. Configure the agent:
   - **Name:** Perseus Memory Agent
   - **Goal:** Help developers maintain persistent project context across sessions
   - **Instructions:** See `docs/agent_instructions.md`

## 4. Connect Elastic MCP Server

1. In Agent Builder, go to **Tools** → **Add Tool** → **MCP Server**
2. Enter your Elastic MCP endpoint URL (from Kibana → Agent Builder → Tools)
3. Authenticate with your Elasticsearch API key
4. Test the connection — you should see Elastic search tools available

## 5. Deploy and Test

1. Click **Deploy** in Agent Builder
2. Use the provided endpoint URL as your `hosted_project_url` in the Devpost submission
3. Test by interacting with the agent through the Agent Builder chat interface

## 6. Environment Variables

Set these in Agent Builder's environment or your `.env` file:

```bash
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
ELASTIC_CLOUD_ID=your-elastic-cloud-id
ELASTIC_API_KEY=your-elastic-api-key
ELASTIC_MEMORY_INDEX=perseus-agent-memory
ELASTIC_MCP_ENDPOINT=https://your-elastic-mcp.example.com
MEMORY_BACKEND=elastic
```
