import os
import sys
import requests
import json
import argparse

# Keycloak parameters
kc_url = "http://51.159.145.175:80/auth/realms/gaia-x/protocol/openid-connect/token"
kc_client_id = "federated-catalogue"
kc_client_secret = "QQ5s1NEc4so3bzdPWaSc71ehq6PLrq1y"
kc_username = "test"
kc_password = "Testtest1!"
kc_grant_type = "password"
kc_scope = "openid"

# Federated Catalogue base URL
fc_base_url = "http://51.159.145.175/api"

def get_auth_token():
    payload = {
        'grant_type': kc_grant_type,
        'client_id': kc_client_id,
        'client_secret': kc_client_secret,
        'scope': kc_scope,
        'username': kc_username,
        'password': kc_password
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(kc_url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Token retrieval failed: {e}")
        return None


def get_all_self_descriptions():
    token = get_auth_token()
    if not token:
        return

    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(f"{fc_base_url}/self-descriptions", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] GET /self-descriptions failed: {e}")
        return None


def get_self_description_by_hash(sd_hash):
    token = get_auth_token()
    if not token:
        return

    headers = {'Authorization': f'Bearer {token}'}
    try:
        url = f"{fc_base_url}/self-descriptions/{sd_hash}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] GET /self-descriptions/{sd_hash} failed: {e}")
        return None

def post_query(statement, parameters=None, query_language="OPENCYPHER"):
    token = get_auth_token()
    if not token:
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    body = {
        "statement": statement,
        "parameters": parameters or {},
    }

    try:
        response = requests.post(f"{fc_base_url}/query", headers=headers, json=body)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] POST /query failed: {e}")
        return None


def post_query_search(statement, parameters=None, query_language="OPENCYPHER", annotations=None):
    token = get_auth_token()
    if not token:
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    body = {
        "statement": statement,
        "parameters": parameters or {},
        "annotations": annotations or {
            "queryLanguage": query_language
        }
    }

    try:
        response = requests.post(f"{fc_base_url}/query/search", headers=headers, json=body)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] POST /query/search failed: {e}")
        return None


def main():
    # Exemple d'utilisation
    print("Listing Self-Descriptions:")
    print(json.dumps(get_all_self_descriptions(), indent=2)) #ok

    # Example POST /query
    print("\nSending query...")
    print(json.dumps(post_query("MATCH (n) RETURN n LIMIT 5"), indent=2)) #ok

    # Example POST /query/search
    print("\nSending distributed search...")
    print(json.dumps(post_query_search("MATCH (n) RETURN n LIMIT 5"), indent=2))
    
    # Example GET /self-descriptions/HASH
    print("\Getting a specific SD by hash...")
    print(json.dumps(get_self_description_by_hash("f5f806698792da113b19c43b45ead220036a6caf8f9963f0068e821afc5d6135"), indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
