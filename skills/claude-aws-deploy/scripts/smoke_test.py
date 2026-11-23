#!/usr/bin/env python3
"""Smoke test for a Claude-on-AWS deployment.

  --bedrock          one Converse call straight to Bedrock (credentials, region, model access)
  --url URL          GET URL/health, then POST a short prompt to URL/ask
Model ID for --bedrock comes from --model or the ANTHROPIC_MODEL env var.
Exit code 1 on failure.
"""
import argparse
import os
import sys
import time


def bedrock_check(model: str, region: str) -> None:
    import boto3
    client = boto3.client("bedrock-runtime", region_name=region)
    t = time.time()
    resp = client.converse(
        modelId=model,
        messages=[{"role": "user", "content": [{"text": "Reply with the single word: ok"}]}],
        inferenceConfig={"maxTokens": 10},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    print(f"bedrock OK in {time.time() - t:.1f}s: {text!r} (usage {resp.get('usage')})")


def app_check(url: str) -> None:
    import requests
    r = requests.get(f"{url}/health", timeout=10)
    r.raise_for_status()
    print("health OK")
    t = time.time()
    r = requests.post(f"{url}/ask", json={"prompt": "Reply with the single word: ok"}, timeout=120)
    r.raise_for_status()
    if not r.text.strip():
        raise RuntimeError("empty response from /ask")
    print(f"ask OK in {time.time() - t:.1f}s")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bedrock", action="store_true")
    p.add_argument("--model", default=os.environ.get("ANTHROPIC_MODEL"))
    p.add_argument("--region", default=os.environ.get("AWS_REGION"))
    p.add_argument("--url")
    a = p.parse_args()
    try:
        if a.bedrock:
            if not (a.model and a.region):
                print("need --model/ANTHROPIC_MODEL and --region/AWS_REGION")
                return 1
            bedrock_check(a.model, a.region)
        if a.url:
            app_check(a.url.rstrip("/"))
        if not (a.bedrock or a.url):
            p.print_help()
            return 1
    except Exception as e:  # noqa: BLE001 - report any failure plainly
        print(f"SMOKE TEST FAILED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
