# -*- coding: utf-8 -*-
"""MCP Server for Cross-Border EU VAT One Stop Shop (MOSS) Reverse-Charge Skill."""
import sys
import json
import logging
from typing import Dict, Any

from .core import EUVATMOSSReverseChargeArbiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "audit_eu_vat_reverse_charge",
        "description": "Determine whether B2B transaction qualifies for Article 196 reverse-charge zero-rated VAT.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buyer_country_code": {
                    "type": "string"
                },
                "seller_country_code": {
                    "type": "string"
                },
                "buyer_vies_vat_number": {
                    "type": "string"
                },
                "is_b2b_verified": {
                    "type": "boolean"
                }
            },
            "required": [
                "buyer_country_code",
                "seller_country_code",
                "is_b2b_verified"
            ]
        }
    },
    {
        "name": "lookup_eu_member_state_vat_rate",
        "description": "Retrieve standard destination VAT rate for B2C consumer digital goods.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "member_state_code": {
                    "type": "string"
                }
            },
            "required": [
                "member_state_code"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-automated-vat-moss-reverse-charge-arbiter-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(EUVATMOSSReverseChargeArbiter, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-agentic-commerce-automated-vat-moss-reverse-charge-arbiter-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
