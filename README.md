# tems-sd-signer

This repository contains a python script that sign a self-description and upload it to the configured Federated Catalogue.

To sign and validate SDs, a private-public key pair is required. To create a self-signed pair this command can be executed:

`openssl req -x509 -newkey rsa:4096 -keyout prk.ss.pem -out cert.ss.pem -sha256 -days 365 -nodes`

## Configuration

Before using the script, you must fill the necessary variables found in the `REQUIRED VARIABLES` part of the [script](src/script.py).

## Usage

To launch the script, use the following command (assuming you are at the root of this repository) :

`python3 src/script.py -sd {path-to-your-self-description} -c {path-to-your-prk-pem}`

Test the get requests : python3 src/get.py 
Upload a file : python3 src/script.py -prk prk.ss.pem -sd template.json


