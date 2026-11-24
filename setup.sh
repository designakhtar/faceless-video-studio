#!/usr/bin/env bash
# Reinstall the studio engine after cloning. Needs Node.js 18+, Python 3.10+, FFmpeg.
set -e
cd "$(dirname "$0")"
npm install --no-fund --no-audit
(cd .tools/google-flow-mcp && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-fund --no-audit)
[ -f .tools/google-flow-mcp/config/flow.config.json ] || cp .tools/google-flow-mcp/config/flow.config.example.json .tools/google-flow-mcp/config/flow.config.json
python3 -m venv .venv
.venv/bin/pip install -q kokoro-onnx soundfile numpy faster-whisper torch transformers
echo "Done. Edit .tools/google-flow-mcp/config/flow.config.json (your Google email, Chrome path)."
