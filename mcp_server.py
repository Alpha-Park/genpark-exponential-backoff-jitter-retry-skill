"""MCP Stdio Server for Exponential Backoff Jitter Retry.
100% Python Standard Library.
"""
import sys
import json
from client import ExponentialBackoffJitterRetry

retry_engine = ExponentialBackoffJitterRetry()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-exponential-backoff-jitter-retry-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "calculate_retry_delay",
                "description": "Calculate backoff delay duration with full, equal, or decorrelated jitter",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "attempt": {"type": "integer"},
                        "base_delay": {"type": "number", "default": 1.0},
                        "max_delay": {"type": "number", "default": 60.0},
                        "strategy": {"type": "string", "enum": ["full_jitter", "equal_jitter", "decorrelated_jitter", "none"], "default": "full_jitter"},
                        "prev_delay": {"type": "number", "default": 1.0}
                    },
                    "required": ["attempt"]
                }
            },
            {
                "name": "simulate_retry_schedule",
                "description": "Simulate end-to-end retry schedule and cumulative wait time",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_attempts": {"type": "integer", "default": 5},
                        "base_delay": {"type": "number", "default": 1.0},
                        "max_delay": {"type": "number", "default": 30.0},
                        "strategy": {"type": "string", "default": "full_jitter"}
                    }
                }
            },
            {
                "name": "should_retry",
                "description": "Evaluate if an HTTP status code or error string is transient/retryable",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer"},
                        "error_message": {"type": "string"}
                    }
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "calculate_retry_delay":
            out = retry_engine.calculate_retry_delay(
                args.get("attempt", 1),
                float(args.get("base_delay", 1.0)),
                float(args.get("max_delay", 60.0)),
                args.get("strategy", "full_jitter"),
                float(args.get("prev_delay", 1.0))
            )
        elif name == "simulate_retry_schedule":
            out = retry_engine.simulate_retry_schedule(
                args.get("max_attempts", 5),
                float(args.get("base_delay", 1.0)),
                float(args.get("max_delay", 30.0)),
                args.get("strategy", "full_jitter")
            )
        elif name == "should_retry":
            out = retry_engine.should_retry(
                args.get("status_code"),
                args.get("error_message", "")
            )
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
