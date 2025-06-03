import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests

######################
# REQUIRED VARIABLES #
######################

# Path to Federated Catalogue signer
jar_path = 'src/resources/signer.jar'

# Keycloak parameters
kc_url = "http://51.159.145.175:80/auth/realms/gaia-x/protocol/openid-connect/token"
kc_client_id = "federated-catalogue"
kc_client_secret = "QQ5s1NEc4so3bzdPWaSc71ehq6PLrq1y"
kc_username = "test"
kc_password = "Testtest1!"
kc_grant_type = "password"
kc_scope = "openid"

# Federated Catalogue parameters
fc_url = "http://51.159.145.175/api/self-descriptions"


###########
# SCRIPT #
###########
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



def remove_all_sd(fc_base_url):
    # Get signed SD path
    # Check if signed self-description is present
    self_descriptions = [
      "36ee1a4c6c1cc19c4aeaab6ab5c7b78a2ae94482581b491028f9cc7103675d4c",
      "af766da45783842acdf7af493c64529ee4d90d2f17a1dc3243857275546fc78a",
      "57435d678f110e882eac5d696a5b690de551a63072ddfea129d20352e6e33fd6",
      "0ebcab5dda35f9a2dc4dad18c9cd983d238b37a3c66a74061e1e46bc0ed89691",
      "09e8d6f672de77744918250987cf082e7b3a7c83d6e22644c59f3d86bb1b1b69",
      "34f7b2d583142365bbc5c42ffda58b8a53c7bfc7e9d2405002a26d74dfb5fbdb",
      "52fb062550b0e52c2460d9d8e527766a478f6d6899dcce2004801a467a0dabdc",
      "3844a44f1f759fd6da7c6ba528c349833577ccebcb7c715405dea9799fad3a6f",
      "4af66a85f14b38ef54b9b331cf03cf0d6c26d38ae0edce669468f5a0d829389e"
    ]
    # Get auth token
    auth_token = get_auth_token()

    # Upload signed SD to the Federated Catalog
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    try:
        for sd_hash in self_descriptions:
          fc_url = f"{fc_base_url}/{sd_hash}"
          response = requests.delete(fc_url, headers=headers)
          response.raise_for_status()
          print(f"Self-description {sd_hash} removed successfully.")
        print("All self-descriptions removed successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error deleting self-description: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None


def main():
    # parser = argparse.ArgumentParser(prog="TEMS Self-Description Signer")
    # Run the JAR file
    # Upload signed SD to the FC
    remove_all_sd(fc_url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
