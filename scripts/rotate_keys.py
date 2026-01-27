#!/usr/bin/env python3
"""Rotate API keys by calling the backend admin endpoint.

Usage:
  python scripts/rotate_keys.py --url http://127.0.0.1:8000 --admin-key currentKey newkey1 newkey2

This calls POST /admin/rotate-keys with JSON {"keys": [...]} and header `x-api-key` set to the admin key.
"""
import argparse
import json
import sys
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="Base URL of backend (e.g. http://127.0.0.1:8000)")
    p.add_argument("--admin-key", required=True, help="Currently valid admin API key to call rotate endpoint")
    p.add_argument("keys", nargs='+', help="New API keys to install")
    args = p.parse_args()

    url = args.url.rstrip('/') + '/admin/rotate-keys'
    headers = {'x-api-key': args.admin_key, 'Content-Type': 'application/json'}
    payload = {'keys': args.keys}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        print('status:', r.status_code)
        print(r.text)
        r.raise_for_status()
    except Exception as e:
        print('failed:', e)
        sys.exit(2)


if __name__ == '__main__':
    main()
