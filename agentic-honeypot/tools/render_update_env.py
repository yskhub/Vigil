"""Simple helper to update a Render service environment variable.

Usage:
  - Set `RENDER_API_KEY` in your shell (your Render account API key).
  - Call: `python tools/render_update_env.py --service-id <SERVICE_ID> --key API_KEY --value <NEW_VALUE>`

This script will replace or create the environment variable for the service and trigger a deploy.
Refer to Render API docs for details: https://render.com/docs/api
"""
import os
import sys
import argparse
import requests

RENDER_API = "https://api.render.com/v1"


def headers(api_key: str):
    return {"Accept": "application/json", "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def get_envs(service_id: str, api_key: str):
    url = f"{RENDER_API}/services/{service_id}/env-vars"
    r = requests.get(url, headers=headers(api_key))
    r.raise_for_status()
    return r.json()


def upsert_env(service_id: str, api_key: str, key: str, value: str, is_secret: bool = True):
    # Render API: POST /services/{serviceId}/env-vars to create, PATCH to update specific var
    envs = get_envs(service_id, api_key)
    existing = next((e for e in envs if e.get("key") == key), None)
    if existing:
        env_id = existing["id"]
        url = f"{RENDER_API}/services/{service_id}/env-vars/{env_id}"
        payload = {"value": value, "isSecret": is_secret}
        r = requests.patch(url, json=payload, headers=headers(api_key))
        r.raise_for_status()
        return r.json()
    else:
        url = f"{RENDER_API}/services/{service_id}/env-vars"
        payload = {"key": key, "value": value, "isSecret": is_secret}
        r = requests.post(url, json=payload, headers=headers(api_key))
        r.raise_for_status()
        return r.json()


def trigger_deploy(service_id: str, api_key: str):
    url = f"{RENDER_API}/services/{service_id}/deploys"
    r = requests.post(url, headers=headers(api_key), json={})
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--value", required=True)
    parser.add_argument("--no-deploy", action="store_true", help="Don't trigger a deploy after updating the var")
    args = parser.parse_args()

    api_key = os.getenv("RENDER_API_KEY")
    if not api_key:
        print("Set RENDER_API_KEY environment variable with your Render API key")
        sys.exit(1)

    print(f"Updating {args.key} for service {args.service_id}...")
    upsert_env(args.service_id, api_key, args.key, args.value)
    print("Updated env var.")
    if not args.no_deploy:
        print("Triggering deploy...")
        trigger_deploy(args.service_id, api_key)
        print("Deploy triggered.")


if __name__ == "__main__":
    main()
