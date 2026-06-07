"""Elastic Memory Proxy — Cloud Function for Agent Builder

Agent Designer doesn't support authenticated MCP servers.
This Cloud Function acts as a proxy, accepting unauthenticated
requests from Agent Builder and forwarding them to Elastic with
the API key embedded.

Deploy via Google Cloud Console → Cloud Functions, or gcloud.
"""

import json
import os
import urllib.request
import urllib.error

ELASTIC_ENDPOINT = os.environ.get(
    "ELASTIC_ENDPOINT",
    "https://your-deployment.es.us-central1.gcp.cloud.es.io:443"
)
ELASTIC_API_KEY = os.environ.get("ELASTIC_API_KEY", "")
MEMORY_INDEX = os.environ.get("MEMORY_INDEX", "perseus-agent-memory")


def handle_request(request):
    """Cloud Function entry point.

    Expects JSON body: {"action": "search|store", ...}
    """
    request_json = request.get_json(silent=True) or {}
    action = request_json.get("action", "search")

    if action == "search":
        return search_memory(request_json)
    elif action == "store":
        return store_memory(request_json)
    elif action == "delete":
        return delete_memory(request_json)
    else:
        return {"error": f"Unknown action: {action}"}, 400


def search_memory(params):
    """Search memory with hybrid semantic + keyword query."""
    query = params.get("query", "")
    project = params.get("project")
    category = params.get("category")
    limit = params.get("limit", 10)

    es_query = {
        "query": {
            "bool": {
                "must": [
                    {"multi_match": {
                        "query": query,
                        "fields": ["content", "content.keyword"],
                        "type": "best_fields"
                    }}
                ],
                "filter": []
            }
        },
        "size": limit,
        "sort": [{"_score": "desc"}, {"created_at": "desc"}]
    }

    if project:
        es_query["query"]["bool"]["filter"].append({"term": {"project": project}})
    if category:
        es_query["query"]["bool"]["filter"].append({"term": {"category": category}})

    return _es_request("POST", f"/{MEMORY_INDEX}/_search", es_query)


def store_memory(params):
    """Store a memory entry in Elasticsearch."""
    doc = {
        "content": params.get("content", ""),
        "category": params.get("category", "fact"),
        "project": params.get("project", ""),
        "tags": params.get("tags", []),
        "confidence": params.get("confidence", 1.0),
        "metadata": params.get("metadata", {}),
    }

    entry_id = params.get("id") or f"mem-{_generate_id()}"
    result = _es_request("PUT", f"/{MEMORY_INDEX}/_doc/{entry_id}", doc)
    result["id"] = entry_id
    return result


def delete_memory(params):
    """Delete a memory entry."""
    entry_id = params.get("id", "")
    return _es_request("DELETE", f"/{MEMORY_INDEX}/_doc/{entry_id}")


def _es_request(method, path, body=None):
    """Forward request to Elasticsearch with API key auth."""
    url = f"{ELASTIC_ENDPOINT}{path}"
    data = json.dumps(body).encode() if body else None

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"ApiKey {ELASTIC_API_KEY}",
            "Content-Type": "application/json",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"Elastic error: {e.code}", "detail": e.read().decode()[:500]}
    except Exception as e:
        return {"error": str(e)}


def _generate_id():
    import hashlib, time
    return hashlib.md5(str(time.time()).encode()).hexdigest()[:12]


# Cloud Functions require a callable named after the entry point
def memory_proxy(request):
    """HTTP Cloud Function entry point."""
    # CORS
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    result, status = handle_request(request)
    headers = {"Access-Control-Allow-Origin": "*"}

    if isinstance(result, tuple):
        return result

    return (json.dumps(result), status, headers)
