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
kc_url = "KC_URL/realms/gaia-x/protocol/openid-connect/token"
kc_client_id = "federated-catalogue"
kc_client_secret = ""
kc_username = ""
kc_password = ""
kc_grant_type = "password"
kc_scope = "openid"

# Federated Catalogue parameters
fc_url = "FC_URL/self-descriptions"


###########
# SCRIPT #
###########

def run_jar(jar_args=None):
    # Check if jar file exists
    if not os.path.isfile(jar_path):
        print(f"Error: JAR file not found at '{jar_path}'")
        return 1

    # Build the command
    command = ['java']

    # Add -jar and the jar path
    command.extend(['-jar', jar_path])

    # Add JAR application arguments if provided
    if jar_args:
        command.extend(jar_args)

    # Print the command that will be executed
    print(f"Executing: {' '.join(command)}")

    try:
        # Execute the command and capture output
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Print stdout and stderr
        print("\nStandard Output:")
        print(process.stdout)

        if process.stderr:
            print("\nStandard Error:")
            print(process.stderr)

        print(f"\nProcess returned with exit code: {process.returncode}")
        return process.returncode

    except Exception as e:
        print(f"Error executing signer JAR: {e}")
        return 1


def get_auth_token():
    payload = {
        'grant_type': kc_grant_type,
        'client_id': kc_client_id,
        'client_secret': kc_client_secret,
        'scope': kc_scope,
        'username': kc_username,
        'password': kc_password
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(kc_url, data=payload, headers=headers)
        response.raise_for_status()
        auth_token = response.json()['access_token']
        return auth_token
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None


def upload_to_fc(path_to_sd):
    # Get signed SD path
    sd_name = path_to_sd[0:path_to_sd.rfind('.')]
    sd_extension = path_to_sd[path_to_sd.rfind('.'):]
    signed_sd = sd_name + ".signed" + sd_extension

    # Check if signed self-description is present
    if not os.path.isfile(signed_sd):
        print(f"Error: Signed SD file not found at '{signed_sd}'")
        return 1

    # Get auth token
    auth_token = get_auth_token()

    # Upload signed SD to the Federated Catalog
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    payload = Path(signed_sd).read_text(encoding='utf-8')

    try:
        response = requests.post(fc_url, data=payload, headers=headers)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error uploading self-description: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None


def main():
    parser = argparse.ArgumentParser(prog="TEMS Self-Description Signer")
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument("-sd", type=str, required=True, help="Path to the self-description file to be signed")
    required_args.add_argument("-prk", type=str, required=True,
                               help="Path to the certificate used to sign the self-description")

    # Get argument in correct format
    args = parser.parse_args()
    sd = "sd=" + args.sd
    cert = "prk=" + args.prk

    jar_args = [sd, cert]

    # Run the JAR file
    run_jar(jar_args)
    # Upload signed SD to the FC
    response_code = upload_to_fc(args.sd)
    if response_code == 201:
        print(f"Upload successful !")
    return 0


if __name__ == "__main__":
    sys.exit(main())
