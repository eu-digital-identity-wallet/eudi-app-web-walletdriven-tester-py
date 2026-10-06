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

from typing import Optional

import jwt
from werkzeug.datastructures.structures import MultiDict

class DocumentRetrievalRequest:
    request_uri: Optional[str] = None
    client_id: Optional[str] = None

    def __init__(self, args: MultiDict[str, str]):
        self.request_uri = args.get("request_uri")
        self.client_id = args.get("client_id")

class DocumentDigests:
    hash: str = None
    label: str = None

    def __init__(self, hash: str = None, label: str = None):
        self.hash = hash
        self.label = label

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentDigests":
        return cls(
            hash=data.get("hash"),
            label=data.get("label"),
        )

class Method:
    type: str = None

    def __init__(self, type: str = None):
        self.type = type

    @classmethod
    def from_dict(cls, data: dict) -> "Method":
        return cls(type=data.get("type"))

class DocumentLocations:
    uri: str = None
    method: Method = None

    def __init__(self, uri: str = None, method: Method = None):
        self.uri = uri
        self.method = method

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentLocations":
        return cls(
            uri=data.get("uri"),
            method=Method.from_dict(data["method"]) if data.get("method") else None,
        )

class DocumentRetrievalRequestObject:
    response_type: str = None
    client_id: str = None
    client_id_scheme: Optional[str] = None
    response_mode: Optional[str] = None
    response_uri: Optional[str] = None
    nonce: str = None
    state: Optional[str] = None
    signatureQualifier: str = None
    documentDigests: list[DocumentDigests]
    documentLocations: list[DocumentLocations]
    hashAlgorithmOID: str = None
    clientData: Optional[str] = None

    def __init__(
            self,
            response_type: str = None,
            client_id: str = None,
            client_id_scheme: str = None,
            response_mode: str = None,
            response_uri: str = None,
            nonce: str = None,
            signature_qualifier: str = None,
            document_digests: list[DocumentDigests] = None,
            document_locations: list[DocumentLocations] = None,
            hash_algorithm_oid: str = None,
    ):
        self.response_type = response_type
        self.client_id = client_id
        self.client_id_scheme = client_id_scheme
        self.response_mode = response_mode
        self.response_uri = response_uri
        self.nonce = nonce
        self.signature_qualifier = signature_qualifier
        self.document_digests = document_digests or []
        self.document_locations = document_locations or []
        self.hash_algorithm_oid = hash_algorithm_oid

    @classmethod
    def from_jwt(cls, jar_object_string: str) -> "DocumentRetrievalRequestObject":
        decoded = jwt.decode(jar_object_string, options={"verify_signature": False})
        return cls.from_dict(decoded)

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentRetrievalRequestObject":
        return cls(
            response_type=data.get("response_type"),
            client_id=data.get("client_id"),
            client_id_scheme=data.get("client_id_scheme"),
            response_mode=data.get("response_mode"),
            response_uri=data.get("response_uri"),
            nonce=data.get("nonce"),
            signature_qualifier=data.get("signatureQualifier"),
            document_digests=[
                DocumentDigests.from_dict(d) for d in data.get("documentDigests", [])
            ],
            document_locations=[
                DocumentLocations.from_dict(l) for l in data.get("documentLocations", [])
            ],
            hash_algorithm_oid=data.get("hashAlgorithmOID"),
        )

class DocumentRetrievalResponse:
    state: Optional[str] = None
    error: Optional[str] = None
    documentWithSignature: Optional[list[str]] = None
    signatureObject: Optional[list[str]] = None

    def __init__(self, state: str = None, error: str = None, documentWithSignature: Optional[list[str]] = None,
                 signatureObject: Optional[list[str]] = None):
        self.state = state
        self.error = error
        self.documentWithSignature = documentWithSignature
        self.signatureObject = signatureObject

    def to_dict(self) -> dict[str, str | None | list[str]]:
        return {
            "state": self.state,
            "signatureObject": self.signatureObject,
            "documentWithSignature": self.documentWithSignature,
            "error": self.error,
        }