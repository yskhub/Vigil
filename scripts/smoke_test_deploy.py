#!/usr/bin/env python3
"""Smoke-test a deployed backend: /health and a sample /events POST.

Usage:
  python scripts/smoke_test_deploy.py --url https://your-backend --api-key secret-key
"""
import argparse
import requests
import json
import sys


SAMPLE_EVENT = {
    "sessionId": "smoke-1",
    "message": {"sender": "scammer", "text": "Your account will be blocked, verify now"},
    "conversationHistory": [],
    "metadata": {"channel": "sms"}
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="Base URL of backend, e.g. https://example.com")
    p.add_argument("--api-key", required=True, help="x-api-key to authenticate")
    args = p.parse_args()

    base = args.url.rstrip('/')
    try:
        h = requests.get(base + '/health', timeout=8)
        print('/health', h.status_code, h.text)
    except Exception as e:
        print('health check failed:', e)
        sys.exit(2)

    headers = {'Content-Type': 'application/json', 'x-api-key': args.api_key}
    try:
        r = requests.post(base + '/events', headers=headers, data=json.dumps(SAMPLE_EVENT), timeout=10)
        print('/events', r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text)
    except Exception as e:
        print('events check failed:', e)
        sys.exit(2)


if __name__ == '__main__':
    main()
