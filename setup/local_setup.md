# Local Setup Guide (Engram-rs Backend)

Zero cloud dependencies. Everything runs on your machine.

## 1. Install Engram-rs

```bash
# One-line install
curl -sSL https://raw.githubusercontent.com/tcconnally/engram-rs/main/scripts/bootstrap.sh | bash

# Or build from source
git clone https://github.com/tcconnally/engram-rs.git
cd engram-rs
cargo build --release
cp target/release/engram ~/.local/bin/
```

## 2. Install Python Dependencies

```bash
cd perseus-rapid-agent
pip install -r requirements.txt
```

## 3. Configure

```bash
cp .env.example .env
# Edit .env — set MEMORY_BACKEND=engram
```

Or export directly:
```bash
export MEMORY_BACKEND=engram
export ENGRAM_BIN=engram
# Engram-rs will create the DB automatically
```

## 4. Verify Engram-rs

```bash
engram health
# Expected: {"status": "ok", "entry_count": 0}
```

## 5. Run the Agent

```bash
python -m agent.main
```

You should see:
```
======================================
  Perseus Memory Agent
  Backend: engram
  Google Cloud Rapid Agent Hackathon 2026
======================================

Memory backend health: ok
  Type: engram-rs

--- Engram-rs Session ---
Recall results:
  [1.00] Perseus uses AGENTS.md files...
  [1.00] Engram-rs is the long-term memory backend...

✅ Demo complete.
```

## Switching to Elastic

When you're ready to use the cloud backend:
```bash
export MEMORY_BACKEND=elastic
export ELASTIC_CLOUD_ID=...
export ELASTIC_API_KEY=...
python -m agent.main
```

Same agent code, different backend. Zero code changes.
