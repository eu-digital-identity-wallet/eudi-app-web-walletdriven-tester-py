# coding: latin-1
###############################################################################
# Copyright (c) 2026 European Commission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

from typing import Tuple

import requests
from requests import Request

from app.core.config import settings
from app.schemas.csc.oauth2 import CredentialCreationRequest
from app.schemas.csc.api import CredentialsListRequest, CredentialsListResponse, CredentialsCreateRequest, \
    CredentialsDeleteRequest, SignaturesSignHashRequest, SignaturesSignHashResponse, CredentialsInfoRequest, \
    CredentialsInfoResponse
from flask import current_app as app

credential_list_endpoint = "/csc/v2/credentials/list"
credential_info_endpoint = "/csc/v2/credentials/info"
credential_create_endpoint = "/csc/v2/credentials/create"
credential_delete_endpoint = "/csc/v2/credentials/delete"
signatures_signhash_endpoint = "/csc/v2/signatures/signHash"

def _get_headers(access_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + access_token
    }

def _csc_credentials_list_request() -> Tuple[str, CredentialsListRequest]:
    url = settings.RS_URL + credential_list_endpoint

    request = CredentialsListRequest(
        credentialInfo=False,
        certificates="single",
        certInfo=True
    )
    return url, request

def _csc_credentials_info_request(credentialId:str) -> Tuple[str, CredentialsInfoRequest]:
    url = settings.RS_URL + credential_info_endpoint

    request = CredentialsInfoRequest(
        credentialID=credentialId,
        certificates="chain",
        certInfo=True
    )
    return url, request

def _csc_credentials_create_request() -> Tuple[str, CredentialsCreateRequest]:
    url = settings.RS_URL + credential_create_endpoint

    credential_creation_request = CredentialCreationRequest(
        certificatePolicy="0.4.0.194112.1.2"
    )
    request = CredentialsCreateRequest(
        credentialCreationRequest=credential_creation_request,
        credentialInfo=True,
        certificates="single",
        certInfo=True
    )
    return url, request

def _csc_credentials_delete_request(credential_id: str) -> Tuple[str, CredentialsDeleteRequest]:
    url = settings.RS_URL + credential_delete_endpoint
    request = CredentialsDeleteRequest(
        credentialID=credential_id
    )
    return url, request

def _csc_signatures_signhash_request(hashes: list[str], credential_id: str, sign_algo: str, hash_algorithm_oid: str) -> Tuple[str, SignaturesSignHashRequest]:
    url = settings.RS_URL + signatures_signhash_endpoint
    request = SignaturesSignHashRequest(
        credentialID=credential_id,
        hashes=hashes,
        hashAlgorithmOID=hash_algorithm_oid,
        signAlgo= sign_algo,
        operationMode="S",
        clientData="12345678"
    )
    return url, request

def preview_csc_req(request_type: str, credential_id: str = None, hashes: list[str] = None, sign_algo: str = None, hash_algorithm_oid: str = None) -> Tuple[str, str]:
    if request_type == "credential_list":
        url, request = _csc_credentials_list_request()
    elif request_type == "credential_info":
        url, request = _csc_credentials_info_request(credential_id)
    elif request_type == "credential_create":
        url, request = _csc_credentials_create_request()
    elif request_type == "credential_delete":
        url, request = _csc_credentials_delete_request(credential_id)
    elif request_type == "signatures_signhash":
        url, request = _csc_signatures_signhash_request(hashes=hashes, credential_id=credential_id, sign_algo=sign_algo, hash_algorithm_oid=hash_algorithm_oid)
    else:
        raise ValueError("Request type not recognized.")

    req = Request(method="POST", url=url, data=request.to_json()).prepare()
    return req.url, req.body

def post_csc_credential_list(access_token: str) -> CredentialsListResponse:
    app.logger.info("Requesting credentials list")

    headers = _get_headers(access_token)
    url, request = _csc_credentials_list_request()

    app.logger.info("Request credentials list: "+request.to_json())

    response = requests.post(url=url, data=request.to_json(), headers=headers)
    if response.status_code == 400:
        message = response.json()["message"]
        app.logger.error("It was impossible to retrieve the credentials list. " + message)
        raise ValueError("It was impossible to retrieve the credentials list: " + message)
    elif response.status_code == 200:
        app.logger.info("Retrieved credentials list.")
        response = CredentialsListResponse.from_json(response.json())
        return response
    else:
        raise ValueError("It was impossible to retrieve the credentials list.")

def post_csc_v2_credentials_info(access_token, credentialId):

    headers = _get_headers(access_token)
    url, request = _csc_credentials_info_request(credentialId)

    response = requests.post(url=url, data=request.to_json(), headers=headers)

    if response.status_code == 400:
        message = response.json()["message"]
        app.logger.error(message)
        raise Exception("It was impossible to retrieve credential info: " + message)

    elif response.status_code == 200:
        info_response = CredentialsInfoResponse.from_json(response.json())
        app.logger.info("Retrieved credential info.")
        return info_response.cert.certificates, info_response.key.algo
    return None

def post_csc_v2_credentials_create(access_token: str):
    app.logger.info("Requesting credentials create.")

    headers = _get_headers(access_token)
    url, request = _csc_credentials_create_request()

    response = requests.post(url=url, data=request.to_json(), headers=headers)

    if response.status_code == 400:
        message = response.json()["message"]
        app.logger.error("It was impossible to create the certificate: " + message)
        raise ValueError("It was impossible to create the certificate: " + message)
    elif response.status_code == 201:
        app.logger.info("Created Certificate.")
    else:
        raise ValueError("Received an unexpected status code when creating the certificate.")

def post_csc_v2_credentials_delete(access_token: str, credential_id: str):
    app.logger.info("Requesting credentials delete.")

    headers = _get_headers(access_token)
    url, request = _csc_credentials_delete_request(credential_id)

    response = requests.post(url=url, data=request.to_json(), headers=headers)
    if response.status_code == 400:
        message = response.json()["message"]
        app.logger.error("It was impossible to delete the certificate: " + message)
        raise ValueError("It was impossible to delete the certificate: " + message)
    elif response.status_code == 204:
        app.logger.info("Deleted Certificate.")
    else:
        raise ValueError("Received an unexpected status code when deleting the certificate.")

def post_csc_v2_signatures_signhash(access_token: str, credential_id: str, hashes: list[str], sign_algo: str, hash_algorithm_oid: str) -> SignaturesSignHashResponse:
    app.logger.info("Requesting signing hash.")

    headers = _get_headers(access_token)
    url, request = _csc_signatures_signhash_request(hashes, credential_id, sign_algo, hash_algorithm_oid)

    response = requests.post(url=url, data=request.to_json(), headers=headers)
    if response.status_code == 200:
        app.logger.info("Successfully signed the hash value")
        return SignaturesSignHashResponse(signatures=response.json()["signatures"])
    else:
        app.logger.error("Error signing hash. Retrieved error message in: " + response.text)
        raise Exception("It was impossible to sign the hash.")
