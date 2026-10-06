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
import base64
from typing import Tuple

import requests
from requests import Request

from app.core.config import settings
from app.schemas.csc.oauth2 import OAuth2CallbackRequest, OAuth2AuthorizeRequest, OAuth2TokenRequest, \
    OAuth2TokenResponse
from flask import current_app as app, session

oauth2_authorize_endpoint = "/oauth2/authorize"
oauth2_token_endpoint = "/oauth2/token"

def _get_oauth2_client_params(authentication: str) -> tuple[str, str, str]:
    client_id = settings.OAUTH_CLIENT_ID
    client_secret = settings.OAUTH_CLIENT_SECRET
    redirect_uri = settings.OAUTH_REDIRECT_URL
    if authentication == "cross":
        client_id = settings.OAUTH_CROSS_DEVICE_FLOW_CLIENT_ID
        client_secret = settings.OAUTH_CROSS_DEVICE_FLOW_CLIENT_SECRET
        redirect_uri = settings.OAUTH_CROSS_DEVICE_FLOW_REDIRECT_URL
    if authentication == "form":
        client_id = settings.OAUTH_TEST_FORM_CLIENT_ID
        client_secret = settings.OAUTH_TEST_FORM_CLIENT_SECRET
        redirect_uri = settings.OAUTH_TEST_FORM_REDIRECT_URL
    return client_id, client_secret, redirect_uri

## OAuth2 Authorize
def _get_requests(scope: str, code_challenge: str, authentication: str = None, credential_id: str = None,
                  numSignatures: int = None, hashes: str = None, hashAlgorithmOID: str = None):
    client_id, client_secret, redirect_uri = _get_oauth2_client_params(authentication)
    if scope == "service":
        request = OAuth2AuthorizeRequest(
            response_type="code",
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope="service",
            code_challenge=code_challenge,
            code_challenge_method=settings.OAUTH_CODE_CHALLENGE_METHOD,
            state=session.sid
        )
        return request
    elif scope == "credential-creation":
        authorization_details = [{"type": "https://cloudsignatureconsortium.org/2025/credential-creation",
                                  "credentialCreationRequest": {"certificatePolicy": "0.4.0.194112.1.2"}}]
        request = OAuth2AuthorizeRequest(
            response_type="code",
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=settings.OAUTH_CODE_CHALLENGE_METHOD,
            state=session.sid,
            authorization_details=str(authorization_details)
        )
        return request
    elif scope == "credential-deletion":
        authorization_details = [{"type": "https://cloudsignatureconsortium.org/2025/credential-deletion", "credentialID": credential_id}]
        request = OAuth2AuthorizeRequest(
            response_type="code",
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=settings.OAUTH_CODE_CHALLENGE_METHOD,
            state=session.sid,
            authorization_details=str(authorization_details)
        )
        return request
    elif scope == "credential":
        request = OAuth2AuthorizeRequest(
            response_type="code",
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope="credential",
            code_challenge=code_challenge,
            code_challenge_method=settings.OAUTH_CODE_CHALLENGE_METHOD,
            state=session.sid,
            numSignatures=numSignatures,
            hashes=hashes,
            hashAlgorithmOID=hashAlgorithmOID,
            credentialID=credential_id,
        )
        return request
    else:
        raise ValueError(f"Unknown scope {scope}")

def _get_oauth2_authorize_request_url(request: OAuth2AuthorizeRequest) -> str:
    url = settings.AS_URL + oauth2_authorize_endpoint
    req = Request(method="GET", url=url, params=request.to_params()).prepare()
    return req.url

def get_oauth2_authorize_request_preview(scope: str, code_challenge: str, authentication: str = None, credential_id: str = None,
                                         numSignatures: int = None, hashes: list[str] = None, hashAlgorithmOID: str = None) -> str:
    hashes_base64_url = None
    if hashes is not None:
        hashes_base64_url = _get_hash_for_oauth2_authorize_credential(hashes)
    request = _get_requests(scope=scope, authentication=authentication, code_challenge=code_challenge, credential_id=credential_id, numSignatures=numSignatures, hashes=hashes_base64_url, hashAlgorithmOID=hashAlgorithmOID)
    return _get_oauth2_authorize_request_url(request)

def _make_oauth2_authorize_request(request: OAuth2AuthorizeRequest) -> Tuple[str, str]:
    url = settings.AS_URL + oauth2_authorize_endpoint
    response = requests.get(url=url, params=request.to_params(), allow_redirects=False)

    if response.status_code == 302:
        jsessionid = response.cookies.get("JSESSIONID")
        location = response.headers["Location"]
        app.logger.info("Retrieved location of authentication endpoint: " + location)
        return location, jsessionid
    elif response.status_code == 400:
        message = response.json()["message"]
        app.logger.error(message)
        raise ValueError("It was impossible to retrieve the authentication link: " + message)
    else:
        raise ValueError("Unexpected status code: " + str(response.status_code))

def oauth2_authorize_service(code_challenge: str, authentication: str) -> Tuple[str, str]:
    request = _get_requests(scope="service", authentication=authentication, code_challenge=code_challenge)
    return _make_oauth2_authorize_request(request)

def oauth2_authorize_credential_create(code_challenge: str, authentication: str) -> Tuple[str, str]:
    request = _get_requests(scope="credential-creation", authentication=authentication, code_challenge=code_challenge)
    return _make_oauth2_authorize_request(request)

def oauth2_authorize_credential_delete(code_challenge: str, authentication: str, credential_id: str) -> Tuple[str, str]:
    request = _get_requests(scope="credential-deletion", authentication=authentication, code_challenge=code_challenge, credential_id=credential_id)
    return _make_oauth2_authorize_request(request)

def _get_hash_for_oauth2_authorize_credential(hashes):
    hashes_base64_url = []
    for h in hashes:
        decoded = base64.b64decode(h)
        base64url = base64.urlsafe_b64encode(decoded).decode('utf-8')
        hashes_base64_url.append(base64url)

    return ",".join(hashes_base64_url)

def oauth2_authorize_credential(code_challenge: str, authentication: str, hashes: list,  credential_id: str, numSignatures: int, hashAlgorithmOID: str):
    hashes_base64_url = _get_hash_for_oauth2_authorize_credential(hashes)
    request = _get_requests(scope="credential", authentication=authentication, code_challenge=code_challenge, numSignatures=numSignatures,
                            credential_id=credential_id, hashes=hashes_base64_url, hashAlgorithmOID=hashAlgorithmOID)
    return _make_oauth2_authorize_request(request)

def validate_callback(params:OAuth2CallbackRequest, code_verifier:str, session_state: str):
    if not code_verifier:
        app.logger.error("Session key 'code_verifier' is missing.")
        raise ValueError("Session expired or invalid request.")
    if params.state != session_state:
        raise ValueError("State mismatch ? possible CSRF attack.")
    if params.error:
        app.logger.error(f"Received Error {params.error}: {params.error_description}")
        raise ValueError(f"Received Error {params.error}: {params.error_description}")
    if params.code is None:
        app.logger.error("No oauth2 authorization code received.")
        raise ValueError("Missing oauth2 authorization code.")

    app.logger.info("Successfully validated oauth2 callback params.")

## OAuth2 Token
def _make_oauth2_token_request(request: OAuth2TokenRequest, client_id: str, client_secret: str) -> OAuth2TokenResponse:
    url = settings.AS_URL + oauth2_token_endpoint
    value_to_encode = f"{client_id}:{client_secret}"
    encoded_value = base64.b64encode(value_to_encode.encode()).decode('utf-8')
    authorization_basic = f"Basic {encoded_value}"
    headers = {
        'Authorization': authorization_basic
    }
    response = requests.post(url=url, params=request.to_params(), headers=headers, allow_redirects=False)
    if response.status_code == 400:
        error = response.json()["error"]
        error_description = response.json()["error_description"]
        app.logger.error("Error in token request: " + error + " - " + error_description)
        raise ValueError("Error while trying to retrieve access: " + error + " - " + error_description)
    elif response.status_code == 200:
        app.logger.info("Successful oauth2 token request: " + str(response.status_code))
        return OAuth2TokenResponse.from_json(response.json())
    else:
        raise ValueError(
            "Unexpected status code (" + str(response.status_code) + ") when trying to retrieve access token.")

def oauth2_token(code_verifier: str, code: str, authentication: str) -> OAuth2TokenResponse:
    client_id, client_secret, redirect_uri = _get_oauth2_client_params(authentication)
    request = OAuth2TokenRequest(
        grant_type="authorization_code",
        code=code,
        client_id= client_id,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
    )
    return _make_oauth2_token_request(request, client_id, client_secret)

def oauth2_token_with_authorization_details(code_verifier: str, code: str, authorization_details, authentication: str) -> OAuth2TokenResponse:
    client_id, client_secret, redirect_uri = _get_oauth2_client_params(authentication)
    request = OAuth2TokenRequest(
        grant_type="authorization_code",
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
        authorization_details=authorization_details
    )
    return _make_oauth2_token_request(request, client_id, client_secret)

def oauth2_token_credential_create(code, code_verifier, authentication):
    authorization_details = [{"type": "https://cloudsignatureconsortium.org/2025/credential-creation",
                              "credentialCreationRequest": {"certificatePolicy": "0.4.0.194112.1.2"}}]
    return oauth2_token_with_authorization_details(code_verifier=code_verifier, code = code,
                                                   authorization_details=authorization_details,
                                                   authentication=authentication)

def oauth2_token_credential_delete(code, code_verifier, credential_id, authentication):
    authorization_details = [
        {"type": "https://cloudsignatureconsortium.org/2025/credential-creation", "credentialID": credential_id}]
    return oauth2_token_with_authorization_details(code_verifier=code_verifier, code=code,
                                                   authorization_details=authorization_details,
                                                   authentication=authentication)

def oauth2_form_login(login_url, username, password, jsessionid):
    response = requests.post(
        login_url,
        data={
            "username": username,
            "password": password
        },
        cookies={"JSESSIONID": jsessionid},
        allow_redirects=False
    )
    new_jsessionid = response.cookies.get("JSESSIONID")
    location = response.headers.get("Location")
    return location, new_jsessionid

def oauth2_authorize_with_given_parameters(jsessionid: str, args: dict) -> str:
    app.logger.info("Making oauth2 authorization as follow up to form login.")
    response = requests.get(
        settings.AS_URL + '/oauth2/authorize',
        params=args,
        cookies={"JSESSIONID": jsessionid},
        allow_redirects=False
    )
    return response.headers.get("Location")