#!/usr/bin/env python3
"""
claude_json_to_text.py
Convert a Claude-style chat-export JSON into a human-readable text file.

Usage:
    python claude_json_to_text.py input.json output.txt
"""

import json
import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def try_parse_timestamp(value: Any) -> Optional[str]:
    if not value:
        return None
    # Common timestamp formats: epoch (int/float), ISO strings
    try:
        if isinstance(value, (int, float)):
            # assume seconds or milliseconds
            ts = float(value)
            if ts > 1e12:
                ts = ts / 1000.0
            return datetime.utcfromtimestamp(ts).isoformat() + "Z"
        if isinstance(value, str):
            # try ISO parse fallback (do not fail hard)
            try:
                # strip microseconds if present
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.isoformat()
            except Exception:
                return value
    except Exception:
        return None
    return None

def extract_text_from_node(node: Any) -> str:
    """
    Recursively extract human text from a node that may be:
    - a string
    - a list of strings or dicts
    - a dict with keys like 'text', 'content', 'parts', 'message', 'payload'
    """
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float, bool)):
        return str(node)
    if isinstance(node, list):
        parts = []
        for item in node:
            t = extract_text_from_node(item)
            if t:
                parts.append(t)
        return "\n".join(parts)
    if isinstance(node, dict):
        # common keys that hold text
        for key in ("text", "content", "message", "body", "raw_text", "value"):
            if key in node and node[key] is not None:
                txt = extract_text_from_node(node[key])
                if txt:
                    return txt
        # some exports use 'parts' or 'items'
        for key in ("parts", "items", "segments", "elements"):
            if key in node and isinstance(node[key], (list, dict)):
                txt = extract_text_from_node(node[key])
                if txt:
                    return txt
        # some content arrays have objects with 'type' and 'text' or 'payload'
        if "type" in node and "text" in node:
            return extract_text_from_node(node["text"])
        # fallback: try to join all string values in dict
        collected = []
        for k, v in node.items():
            if isinstance(v, (str, int, float, bool)):
                collected.append(f"{k}: {v}")
            else:
                nested = extract_text_from_node(v)
                if nested:
                    collected.append(f"{k}: {nested}")
        return "\n".join(collected).strip()
    return ""

def normalize_author(msg: Dict[str, Any]) -> str:
    for key in ("author", "role", "sender", "from", "user"):
        if key in msg and msg[key]:
            val = msg[key]
            if isinstance(val, dict):
                # sometimes author: { "role": "assistant", "name": "Claude" }
                if "role" in val:
                    return val.get("role") or val.get("name") or str(val)
                if "name" in val:
                    return val.get("name")
                return json.dumps(val, ensure_ascii=False)
            return str(val)
    # fallback heuristics
    if "is_assistant" in msg:
        return "assistant" if msg.get("is_assistant") else "user"
    return "unknown"

def find_messages_container(data: Any) -> List[Dict[str, Any]]:
    """
    Try to find a list of message-like dicts in the JSON.
    """
    if isinstance(data, list):
        # maybe it's already a list of messages
        if all(isinstance(x, dict) for x in data):
            return data
    if isinstance(data, dict):
        # common top-level keys
        for key in ("conversations", "messages", "items", "chat", "threads", "history"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # sometimes nested under 'export' or 'data'
        for key in ("data", "export"):
            if key in data and isinstance(data[key], (list, dict)):
                found = find_messages_container(data[key])
                if found:
                    return found
        # fallback: if dict contains many dict children that look like messages
        candidate = []
        for k, v in data.items():
            if isinstance(v, dict):
                # heuristic: contains 'content' or 'text' or 'author'
                if any(sub in v for sub in ("content", "text", "author", "role", "message")):
                    candidate.append(v)
        if candidate:
            return candidate
    return []

def format_message(msg: Dict[str, Any]) -> str:
    author = normalize_author(msg)
    # timestamp heuristics
    ts = None
    for key in ("create_time", "created_at", "timestamp", "time", "date"):
        if key in msg:
            ts = try_parse_timestamp(msg[key])
            if ts:
                break
    # extract text from common fields
    text = ""
    # common shapes: msg["content"], msg["content"][0]["text"], msg["content"]["parts"], msg["text"]
    for key in ("content", "text", "message", "body", "payload"):
        if key in msg and msg[key] is not None:
            text = extract_text_from_node(msg[key])
            if text:
                break
    # some exports use 'content' as list of dicts with 'type' and 'text'
    if not text:
        # try entire message dict
        text = extract_text_from_node(msg)
    # attachments or non-text payloads
    attachments = []
    for key in ("attachments", "files", "media", "images"):
        if key in msg and msg[key]:
            attachments.append(f"{key}: {json.dumps(msg[key], ensure_ascii=False)}")
    # code blocks detection: keep triple-backtick blocks if present
    if not text and attachments:
        text = "\n".join(attachments)
    header = f"=== {ts or 'no-timestamp'} | {author} ==="
    body = text.strip() or "[no textual content found]"
    return f"{header}\n{body}\n\n"

def convert(input_path: str, output_path: str) -> None:
    data = load_json(input_path)
    messages = find_messages_container(data)
    # if nothing found, try to treat top-level as single conversation
    if not messages:
        # try to find nested messages under any dict value
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    messages = v
                    break
    # final fallback: wrap top-level dict as single message
    if not messages:
        messages = [data] if isinstance(data, dict) else []
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"Converted from: {os.path.basename(input_path)}\n\n")
        if not messages:
            out.write("No message-like structures found. Raw JSON dump below.\n\n")
            out.write(json.dumps(data, ensure_ascii=False, indent=2))
            return
        for idx, msg in enumerate(messages, start=1):
            try:
                formatted = format_message(msg)
            except Exception as e:
                formatted = f"=== message {idx} | parse-error ===\nParse error: {e}\nRaw: {json.dumps(msg, ensure_ascii=False)}\n\n"
            out.write(formatted)

def main():
    if len(sys.argv) < 3:
        print("Usage: python claude_json_to_text.py input.json output.txt")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    try:
        convert(input_path, output_path)
        print(f"Converted {input_path} -> {output_path}")
    except Exception as e:
        print("Error during conversion:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()
