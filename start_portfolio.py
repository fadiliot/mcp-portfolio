import os
import sys
import socket
import uvicorn
from pathlib import Path

# Ensure root directory is on pythonpath
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configure utf-8 encoding for Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def find_available_port(start_port: int = 8000, max_port: int = 8090) -> int:
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port

if __name__ == "__main__":
    port = int(os.environ.get("PORT", find_available_port(8000)))
    
    print("\n" + "=" * 65)
    print(" [*] FADIL ANWAR - MODEL CONTEXT PROTOCOL (MCP) PORTFOLIO SERVER")
    print("=" * 65)
    print(f" > Web Dashboard & UI:  http://127.0.0.1:{port}/")
    print(f" > Live MCP Endpoint:   http://127.0.0.1:{port}/mcp")
    print(f" > Live SSE Endpoint:   http://127.0.0.1:{port}/sse")
    print(f" > REST Health Check:   http://127.0.0.1:{port}/api/health")
    print("-" * 65)
    print(" To connect Claude Code CLI:")
    print(f"   claude mcp add --transport http fadil-portfolio http://127.0.0.1:{port}/mcp")
    print("=" * 65 + "\n")

    uvicorn.run(
        "server.mcp_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
