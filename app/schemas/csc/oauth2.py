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

import json
from typing import Optional, List
from werkzeug.datastructures.structures import MultiDict

class OAuth2CallbackRequest:
    code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None
    error_uri: Optional[str] = None

    def __init__(self, args: MultiDict[str, str]):
        self.code = args.get("code")
        self.state = args.get("state")
        self.error = args.get("error")
        self.error_description = args.get("error_description")
        self.error_uri = args.get("error_uri")

class CredentialCreationRequest:
    certificatePolicy: str = None
    subjectData: Optional[str] = None

    def __init__(self, certificatePolicy: str, subjectData: str = None):
        self.certificatePolicy = certificatePolicy
        self.subjectData = subjectData

    def to_json(self) -> str:
        filtered_data = {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }
        return json.dumps(filtered_data)

class CredentialCreationAuthorizationDetails:
    type: str = None
    acr_values: Optional[str] = None
    credentialCreationRequest: CredentialCreationRequest = None

class CredentialDeletionAuthorizationDetails:
    type: str = None
    credentialID: str = None

class DocumentInfo:
    label: Optional[str] = None
    hash: str = None
    hashType: Optional[str] = None
    signed_props: Optional[str] = None
    circumstantialData: Optional[str] = None

class CredentialAuthorizationDetails:
    type: str = None
    locations: Optional[List[str]] = None
    credentialID: Optional[str] = None
    signatureQualifier: Optional[str] = None
    numSignatures: int = None
    documentDigests: List[DocumentInfo] = []
    hashAlgorithmOID: str = None

class OAuth2AuthorizeRequest:
    response_type: str = None
    client_id: str = None
    redirect_uri: Optional[str] = None
    scope: Optional[str] = None
    authorization_details: Optional[str] = None
    code_challenge: str = None
    code_challenge_method: Optional[str] = None
    state: Optional[str] = None
    request_uri: Optional[str] = None
    lang: Optional[str] = None
    clientData: Optional[str] = None

    # scope = credential
    credentialID: Optional[str] = None
    signatureQualifier: Optional[str] = None
    numSignatures: Optional[int] = None
    hashes: Optional[str] = None
    hashAlgorithmOID: Optional[str] = None
    description: Optional[str] = None
    account_token: Optional[str] = None

    def __init__(self, response_type: str, client_id: str, code_challenge: str, redirect_uri: Optional[str] = None,
        authorization_details: Optional[str] = None, scope: Optional[str] = None, code_challenge_method: Optional[str] = None,
        state: Optional[str] = None, request_uri: Optional[str] = None, lang: Optional[str] = None,
        clientData: Optional[str] = None, credentialID: Optional[str] = None, signatureQualifier: Optional[str] = None,
        numSignatures: Optional[int] = None, hashes: Optional[str] = None, hashAlgorithmOID: Optional[str] = None,
        description: Optional[str] = None, account_token: Optional[str] = None,
    ):
        self.response_type = response_type
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.authorization_details = authorization_details
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.state = state
        self.request_uri = request_uri
        self.lang = lang
        self.clientData = clientData
        self.credentialID = credentialID
        self.signatureQualifier = signatureQualifier
        self.numSignatures = numSignatures
        self.hashes = hashes
        self.hashAlgorithmOID = hashAlgorithmOID
        self.description = description
        self.account_token = account_token

    def to_params(self) -> dict:
        return {k: v for k, v in {
            "response_type": self.response_type,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "authorization_details": self.authorization_details,
            "code_challenge": self.code_challenge,
            "code_challenge_method": self.code_challenge_method,
            "state": self.state,
            "request_uri": self.request_uri,
            "lang": self.lang,
            "clientData": self.clientData,

            "credentialID": self.credentialID,
            "signatureQualifier": self.signatureQualifier,
            "numSignatures": self.numSignatures,
            "hashes": self.hashes,
            "hashAlgorithmOID": self.hashAlgorithmOID,
            "description": self.description,
            "account_token": self.account_token,
        }.items() if v is not None}

class OAuth2TokenRequest:
    grant_type: str = None
    code: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: str = None
    client_secret: Optional[str] = None
    client_assertion: Optional[str] = None
    client_assertion_type: Optional[str] = None
    redirect_uri: Optional[str] = None
    authorization_details: Optional[str] = None
    code_verifier: Optional[str] = None
    client_data: Optional[str] = None

    def __init__(self, grant_type: str, client_id: str, code: Optional[str] = None, refresh_token: Optional[str] = None,
            client_secret: Optional[str] = None, client_assertion: Optional[str] = None, client_assertion_type: Optional[str] = None,
            redirect_uri: Optional[str] = None, authorization_details: Optional[str] = None, client_data: Optional[str] = None,
            code_verifier: Optional[str] = None,
        ):
        self.grant_type = grant_type
        self.client_id = client_id
        self.code = code
        self.refresh_token = refresh_token
        self.client_secret = client_secret
        self.client_assertion = client_assertion
        self.client_assertion_type = client_assertion_type
        self.redirect_uri = redirect_uri
        self.authorization_details = authorization_details
        self.code_verifier = code_verifier
        self.client_data = client_data

    def to_params(self) -> dict:
        return {k: v for k, v in {
            "grant_type": self.grant_type,
            "code": self.code,
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "authorization_details": self.authorization_details,
            "code_verifier": self.code_verifier,
            "clientData": self.client_data,
        }.items() if v is not None}

class OAuth2TokenResponse:
    access_token: str = None
    refresh_token: Optional[str] = None
    token_type: str = None
    expires_in: Optional[int] = None
    credentialID: Optional[str] = None
    authorization_details: Optional[str] = None
    scope: Optional[str] = None

    def __init__(self, access_token: str, refresh_token: str, token_type: str, expires_in: int, credentialID: Optional[str] = None,
                 authorization_details: Optional[str] = None, scope: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.credentialID = credentialID
        self.authorization_details = authorization_details
        self.scope = scope

    @classmethod
    def from_json(cls, data: dict) -> "OAuth2TokenResponse":
        return cls(
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type"),
            expires_in=data.get("expires_in"),
            credentialID=data.get("credentialID"),
            authorization_details= data.get("authorization_details"),
            scope=data.get("scope"),
        )

