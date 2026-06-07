"""Elastic Memory Proxy for Agent Builder.

Deploy as Cloud Function 2nd gen (Cloud Run) — includes Flask server.
Handles Elastic auth internally since Agent Designer doesn't support MCP auth.
"""

import json
import os
import urllib.request
import urllib.error
import hashlib
import time

from flask import Flask, request, jsonify

app = Flask(__name__)

# Read env vars
ES_ENDPOINT = os.environ.get("ELASTIC_ENDPOINT", "")
ES_KEY = os.environ.get("ELASTIC_API_KEY", "")
ES_INDEX = os.environ.get("MEMORY_INDEX", "perseus-agent-memory")


@app.route("/", methods=["POST", "OPTIONS"])
def memory_proxy():
    """Cloud Function entry point — handles all memory operations."""
    if request.method == "OPTIONS":
        return "", 204, {"Access-Control-Allow-Origin": "*"}

    body = request.get_json(silent=True) or {}
    action = body.get("action", "search")

    if action == "store":
        return _handle_store(body)
    elif action == "delete":
        return _handle_delete(body)
    else:
        return _handle_search(body)


def _handle_search(body):
    query = body.get("query", "")
    project = body.get("project")
    category = body.get("category")
    limit = body.get("limit", 10)

    esq = {
        "query": {
            "bool": {
                "must": [{
                    "multi_match": {
                        "query": query,
                        "fields": ["content", "content.keyword"],
                        "type": "best_fields"
                    }
                }],
                "filter": []
            }
        },
        "size": limit,
        "sort": [{"_score": "desc"}]
    }
    if project:
        esq["query"]["bool"]["filter"].append({"term": {"project": project}})
    if category:
        esq["query"]["bool"]["filter"].append({"term": {"category": category}})

    return jsonify(_es("POST", f"/{ES_INDEX}/_search", esq))


def _handle_store(body):
    doc = {
        "content": body.get("content", ""),
        "category": body.get("category", "fact"),
        "project": body.get("project", ""),
        "tags": body.get("tags", []),
        "confidence": body.get("confidence", 1.0),
        "metadata": body.get("metadata", {}),
    }
    eid = body.get("id") or ("mem-" + hashlib.md5(str(time.time()).encode()).hexdigest()[:12])
    result = _es("PUT", f"/{ES_INDEX}/_doc/{eid}", doc)
    result["id"] = eid
    return jsonify(result)


def _handle_delete(body):
    eid = body.get("id", "")
    return jsonify(_es("DELETE", f"/{ES_INDEX}/_doc/{eid}"))


def _es(method, path, body=None):
    """Forward request to Elasticsearch."""
    url = f"{ES_ENDPOINT}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"ApiKey {ES_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"Elastic {e.code}", "detail": e.read().decode()[:300]}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
