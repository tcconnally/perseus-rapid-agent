# Elastic Cloud Setup Guide

## 1. Create Elastic Cloud Account

1. Go to [cloud.elastic.co/registration](https://cloud.elastic.co/registration)
2. Sign up for a **free 14-day trial** (no credit card needed for trial)
3. Create a **Serverless Elasticsearch project**
4. Choose **Google Cloud** as your cloud provider
5. Pick your preferred region (match your GCP region if possible)

## 2. Enable Agent Builder

1. In Kibana, navigate to **Search** → **Agent Builder**
2. Click **Enable Agent Builder**
3. Wait for the setup to complete (~2 minutes)

## 3. Get Your Credentials

From the Elastic Cloud console:

```bash
# Your Cloud ID (found in the deployment details)
ELASTIC_CLOUD_ID=your-deployment-name:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlv...
```

From Kibana → Stack Management → API Keys:
```bash
# Create an API key with appropriate permissions
ELASTIC_API_KEY=your-base64-encoded-api-key
```

## 4. Get MCP Endpoint

In Kibana → Agent Builder → **Tools** tab:
1. Click **MCP Server** 
2. Copy the **MCP endpoint URL**
3. This is your `ELASTIC_MCP_ENDPOINT`

## 5. Create the Memory Index

In Kibana Dev Tools console:

```json
PUT perseus-agent-memory
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "content": { 
        "type": "text",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "category": { "type": "keyword" },
      "project": { "type": "keyword" },
      "tags": { "type": "keyword" },
      "confidence": { "type": "float" },
      "source_session": { "type": "keyword" },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" },
      "metadata": { "type": "object", "enabled": false }
    }
  }
}
```

## 6. Define Agent Tools (MCP)

In Kibana → Agent Builder → **Tools**:

### Search Tool
```json
{
  "name": "search_memory",
  "description": "Search agent memory using hybrid semantic + keyword search",
  "type": "search",
  "index": "perseus-agent-memory",
  "query_field": "content",
  "filters": ["project", "category", "tags"]
}
```

### Store Tool
```json
{
  "name": "store_memory",
  "description": "Store a new memory entry",
  "type": "index",
  "index": "perseus-agent-memory"
}
```

### Delete Tool
```json
{
  "name": "delete_memory",
  "description": "Remove a memory entry by ID",
  "type": "delete",
  "index": "perseus-agent-memory"
}
```

## 7. Test the Connection

```bash
curl -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
  "${ELASTIC_MCP_ENDPOINT}/health"
```

Expected: `{"status": "ok"}`
