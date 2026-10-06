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
from typing import Optional
from flask import current_app as app

from app.schemas.csc.oauth2 import CredentialCreationRequest

class CredentialsCreateRequest:
    credentialCreationRequest: CredentialCreationRequest = None
    credentialInfo: Optional[bool] = False
    certificates: Optional[str] = None
    certInfo: Optional[bool] = None
    authData: Optional[list] = None

    def __init__(self, credentialCreationRequest: CredentialCreationRequest, credentialInfo: bool = False,
                 certificates: str = None, certInfo: bool = False, authData: list = None):
        self.credentialCreationRequest = credentialCreationRequest
        self.credentialInfo = credentialInfo
        self.certificates = certificates
        self.certInfo = certInfo
        self.authData = authData

    def to_json(self) -> str:
        def serialize(value):
            if hasattr(value, "to_json"):
                return json.loads(value.to_json())
            return value

        return json.dumps({
            k: serialize(v)
            for k, v in self.__dict__.items()
            if v is not None
        })

# Auxiliar
class CredentialDeletionRequest:
    credentialID: str = None
    revoke: Optional[bool] = None
    revocationReason: Optional[int] = None

    def __init__(self, credentialID: str, revoke: bool = None, revocationReason: int = None):
        self.credentialID = credentialID
        self.revoke = revoke
        self.revocationReason = revocationReason

    def to_json(self) -> str:
        filtered_data = {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }
        return json.dumps(filtered_data)

class CredentialsDeleteRequest:
    credentialDeletionRequest: CredentialDeletionRequest = None

    def __init__(self, credentialID: str, revoke: bool = None, revocationReason: int = None):
        self.credentialDeletionRequest = CredentialDeletionRequest(credentialID, revoke, revocationReason)

    def to_json(self) -> str:
        def serialize(value):
            if hasattr(value, "to_json"):
                return json.loads(value.to_json())
            return value

        return json.dumps({
            k: serialize(v)
            for k, v in self.__dict__.items()
            if v is not None
        })

class CredentialsListRequest:
    userID: Optional[str] = None
    credentialInfo: Optional[bool] = None
    certificates: Optional[str] = None
    certInfo: Optional[bool] = None
    authInfo: Optional[bool] = None
    onlyValid: Optional[bool] = None
    lang: Optional[str] = None
    clientData: Optional[str] = None

    def __init__(self, userID: str = None, credentialInfo: bool = None, certificates: str = None, certInfo: bool = None,
                 authInfo: bool = None, onlyValid: bool = None, lang: str = None, clientData: str = None):
        self.userID = userID
        self.credentialInfo = credentialInfo
        self.certificates = certificates
        self.certInfo = certInfo
        self.authInfo = authInfo
        self.onlyValid = onlyValid
        self.lang = lang
        self.clientData = clientData

    def to_json(self) -> str:
        filtered_data = {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }
        return json.dumps(filtered_data)

# Auxiliar
class CredentialKey:
    status: str
    algo: list[str]
    len: int
    curve: Optional[str]

    def __init__(
        self,
        status: str,
        algo: list[str],
        length: int,
        curve: Optional[str] = None,
    ):
        self.status = status
        self.algo = algo
        self.len = length
        self.curve = curve

    @classmethod
    def from_json(cls, data: dict):
        if not data:
            return None

        try:
            return cls(
                status=data["status"],
                algo=data["algo"],
                length=data["len"],
                curve=data.get("curve"),
            )
        except KeyError as e:
            app.logger.error(f"Missing key field {e} in {data}")
            return None

# Auxiliar
class CredentialCert:
    certificates: Optional[list[str]]
    status: Optional[str]
    issuer_dn: Optional[str]
    serial_number: Optional[str]
    subject_dn: Optional[str]
    valid_from: Optional[str]
    valid_to: Optional[str]

    def __init__(
        self,
        certificates: Optional[list[str]] = None,
        status: Optional[str] = None,
        issuer_dn: Optional[str] = None,
        serial_number: Optional[str] = None,
        subject_dn: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
    ):
        self.certificates = certificates
        self.status = status
        self.issuer_dn = issuer_dn
        self.serial_number = serial_number
        self.subject_dn = subject_dn
        self.valid_from = valid_from
        self.valid_to = valid_to

    @classmethod
    def from_json(cls, data: dict):
        if not data:
            return None

        try:
            return cls(
                certificates=data.get("certificates"),
                status=data.get("status"),
                issuer_dn=data.get("issuerDN"),
                serial_number=data.get("serialNumber"),
                subject_dn=data.get("subjectDN"),
                valid_from=data.get("validFrom"),
                valid_to=data.get("validTo"),
            )
        except KeyError as e:
            app.logger.error(f"Missing cert field {e} in {data}")
            return None

# Auxiliar
class CredentialAuth:
    mode: str
    expression: Optional[str]
    objects: Optional[list]

    def __init__(
        self,
        mode: str,
        expression: Optional[str] = None,
        objects: Optional[list] = None,
    ):
        self.mode = mode
        self.expression = expression
        self.objects = objects

    @classmethod
    def from_json(cls, data: dict):
        if not data:
            return None
        try:
            return cls(
                mode=data["mode"],
                expression=data.get("expression"),
                objects=data.get("objects"),
            )
        except KeyError as e:
            app.logger.error(f"Missing auth field {e} in {data}")
            return None

# Auxiliar
class CredentialInfo:
    credential_id: str
    key: CredentialKey
    cert: CredentialCert
    auth: CredentialAuth
    multisign: int
    description: Optional[str]
    signature_qualifier: Optional[str]
    scal: Optional[str]
    lang: Optional[str]

    def __init__(
        self,
        credential_id: str,
        key: CredentialKey,
        cert: CredentialCert,
        auth: CredentialAuth,
        multisign: int,
        description: Optional[str] = None,
        signature_qualifier: Optional[str] = None,
        scal: Optional[str] = None,
        lang: Optional[str] = None,
    ):
        self.credential_id = credential_id
        self.key = key
        self.cert = cert
        self.auth = auth
        self.multisign = multisign
        self.description = description
        self.signature_qualifier = signature_qualifier
        self.scal = scal
        self.lang = lang

    @classmethod
    def from_json(cls, data: dict) -> "CredentialInfo":
        return cls(
            credential_id=data["credentialID"],
            description=data.get("description"),
            signature_qualifier=data.get("signatureQualifier"),
            key=CredentialKey.from_json(data["key"]),
            cert=CredentialCert.from_json(data["cert"]),
            auth=CredentialAuth.from_json(data["auth"]),
            scal=data.get("SCAL"),
            multisign=data["multisign"],
            lang=data.get("lang"),
        )

class CredentialsListResponse:
    credential_ids: list[str]
    credential_infos: Optional[list[CredentialInfo]]
    only_valid: Optional[bool]

    def __init__(
        self,
        credential_ids: list[str],
        only_valid: Optional[bool] = None,
        credential_infos: Optional[list[CredentialInfo]] = None,
    ):
        if not credential_ids:
            raise ValueError("'credential_ids' is required and cannot be empty")

        self.credential_ids = credential_ids
        self.credential_infos = credential_infos
        self.only_valid = only_valid

    @classmethod
    def from_json(cls, data: dict) -> "CredentialsListResponse":
        return cls(
            credential_ids=data["credentialIDs"],
            only_valid=data.get("onlyValid"),
            credential_infos=[
                CredentialInfo(**info) for info in data["credentialInfos"]
            ] if data.get("credentialInfos") else None,
        )

class CredentialsInfoRequest:
    credentialID: str
    certificates: Optional[str] = None
    certInfo: Optional[bool] = None
    authInfo: Optional[bool] = None
    lang: Optional[str] = None
    clientData: Optional[str] = None

    def __init__(self, credentialID: str, certificates: Optional[str] = None, certInfo: Optional[bool] = None,
                 authInfo: Optional[bool] = None, lang: Optional[str] = None, clientData: Optional[str] = None):
        self.credentialID = credentialID
        self.certificates = certificates
        self.certInfo = certInfo
        self.authInfo = authInfo
        self.lang = lang
        self.clientData = clientData

    def to_json(self) -> str:
        filtered_data = {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }
        return json.dumps(filtered_data)

class CredentialCertInfoResponse:
    certificates: Optional[list[str]]
    status: Optional[str]
    issuer_dn: Optional[str]
    serial_number: Optional[str]
    subject_dn: Optional[str]
    valid_from: Optional[str]
    valid_to: Optional[str]
    qc_statements: list[str]
    policy: Optional[list[str]]

    def __init__(
        self,
        certificates: Optional[list[str]] = None,
        status: Optional[str] = None,
        issuer_dn: Optional[str] = None,
        serial_number: Optional[str] = None,
        subject_dn: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
        qc_statements: list[str] = None,
        policy: Optional[list[str]] = None
    ):
        self.certificates = certificates
        self.status = status
        self.issuer_dn = issuer_dn
        self.serial_number = serial_number
        self.subject_dn = subject_dn
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.qc_statements = qc_statements
        self.policy = policy

    @classmethod
    def from_json(cls, data: dict):
        if not data:
            return None
        try:
            return cls(
                certificates=data.get("certificates"),
                status=data.get("status"),
                issuer_dn=data.get("issuerDN"),
                serial_number=data.get("serialNumber"),
                subject_dn=data.get("subjectDN"),
                valid_from=data.get("validFrom"),
                valid_to=data.get("validTo"),
                qc_statements=data.get("qcStatements"),
                policy=data.get("policy")
            )
        except KeyError as e:
            app.logger.error(f"Missing cert field {e} in {data}")
            return None

class CredentialsInfoResponse:
    description: Optional[str]
    signature_qualifier: Optional[str]
    key: CredentialKey
    cert: CredentialCertInfoResponse
    auth: CredentialAuth
    SCAL: Optional[str]
    multisign: int
    lang: Optional[str]

    def __init__(self, description: str=None, signature_qualifier: Optional[str]=None, key: Optional[CredentialKey] = None,
                 cert: Optional[CredentialCertInfoResponse] = None, auth: Optional[CredentialAuth] = None, SCAL: Optional[str]=None,
                 multisign: Optional[int] = None, lang: Optional[str] = None):
        self.description = description
        self.signature_qualifier = signature_qualifier
        self.key = key
        self.cert = cert
        self.auth = auth
        self.SCAL = SCAL
        self.multisign = multisign
        self.lang = lang

    @classmethod
    def from_json(cls, data: dict) -> "CredentialsInfoResponse":
        return cls(
            description=data.get("description"),
            signature_qualifier=data.get("signatureQualifier"),
            key=CredentialKey.from_json(data.get("key")),
            cert=CredentialCertInfoResponse.from_json(data.get("cert")),
            auth=CredentialAuth.from_json(data.get("auth")),
            SCAL=data.get("SCAL"),
            multisign=data.get("multisign"),
            lang=data.get("lang")
        )

class SignaturesSignHashRequest:
    signAlgo: str = None
    signAlgoParams: Optional[str]
    credentialID: str = None
    SAD: Optional[str]
    hashes: list[str] = []
    hashAlgorithmOID: Optional[str]
    operationMode: Optional[str]
    validity_period: Optional[int]
    response_uri: Optional[str]
    clientData: Optional[str]

    def __init__(self, signAlgo: str, signAlgoParams: Optional[str] = None, credentialID: str = None, SAD: Optional[str] = None, hashes: list[str] = None,
                 hashAlgorithmOID: Optional[str] = None, operationMode: Optional[str] = None, validity_period: Optional[int] = None,
                 response_uri: Optional[str] = None, clientData: Optional[str] = None):
        self.signAlgo = signAlgo
        self.signAlgoParams = signAlgoParams
        self.credentialID = credentialID
        self.SAD = SAD
        self.hashes = hashes
        self.hashAlgorithmOID = hashAlgorithmOID
        self.operationMode = operationMode
        self.validity_period = validity_period
        self.response_uri = response_uri
        self.clientData = clientData


    def to_json(self) -> str:
        filtered_data = {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }
        return json.dumps(filtered_data)

class SignaturesSignHashResponse:
    signatures: list[str] = []
    responseID: Optional[str] = None

    def __init__(self, signatures: list[str], responseID: Optional[str] = None):
        self.signatures = signatures
        self.responseID = responseID
