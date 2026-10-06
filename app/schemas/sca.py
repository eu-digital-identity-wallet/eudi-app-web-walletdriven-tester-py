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

VALID_SIGNATURE_FORMATS = {"P", "C", "X", "J"}
VALID_CONFORMANCE_LEVELS = {"Ades-B-B", "Ades-B-T", "Ades-B-LT", "Ades-B-LTA"}
VALID_SIGNED_ENVELOPE_PROPERTIES = {"ENVELOPED", "ENVELOPING", "DETACHED", "INTERNALLY_DETACHED"}
VALID_CONTAINERS = {"No", "ASiC-E", "ASiC-S"}

class DocumentsSignDocRequest:
    document: str
    document_name: Optional[str]
    signature_format: Optional[str]
    conformance_level: str
    signed_props: Optional[list]
    signed_envelope_property: Optional[str]
    container: str

    def __init__(
        self,
        document: str,
        document_name: Optional[str] = None,
        signature_format: Optional[str] = None,
        conformance_level: str = "AdES-B-B",
        signed_props: Optional[list] = None,
        signed_envelope_property: Optional[str] = None,
        container: str = "No",
    ):
        if not document:
            raise ValueError("The document must be present in the request")
        if signature_format is not None and signature_format not in VALID_SIGNATURE_FORMATS:
            raise ValueError(f"Invalid signature format '{signature_format}'. Must be one of {VALID_SIGNATURE_FORMATS}")
        if conformance_level not in VALID_CONFORMANCE_LEVELS:
            raise ValueError(f"Invalid conformance level '{conformance_level}'. Must be one of {VALID_CONFORMANCE_LEVELS}")
        if signed_envelope_property is not None and signed_envelope_property not in VALID_SIGNED_ENVELOPE_PROPERTIES:
            raise ValueError(f"Invalid signed envelope property '{signed_envelope_property}'. Must be one of {VALID_SIGNED_ENVELOPE_PROPERTIES}")
        if container not in VALID_CONTAINERS:
            raise ValueError(f"Invalid container '{container}'. Must be one of {VALID_CONTAINERS}")

        self.document = document
        self.document_name = document_name
        self.signature_format = signature_format
        self.conformance_level = conformance_level
        self.signed_props = signed_props or []
        self.signed_envelope_property = signed_envelope_property
        self.container = container

class CalculateHashRequest:
    documents: list[DocumentsSignDocRequest]
    end_entity_certificate: str
    certificate_chain: list[str]
    hash_algorithm_oid: str

    def __init__(
        self,
        documents: list[DocumentsSignDocRequest],
        end_entity_certificate: str,
        hash_algorithm_oid: str,
        certificate_chain: Optional[list[str]] = None,
    ):
        if not documents:
            raise ValueError("At least one document must be present in the request")
        if not end_entity_certificate:
            raise ValueError("The certificate must be present")
        if not hash_algorithm_oid:
            raise ValueError("The hashAlgorithmOID must be present")

        self.documents = documents
        self.end_entity_certificate = end_entity_certificate
        self.hash_algorithm_oid = hash_algorithm_oid
        self.certificate_chain = certificate_chain or []

    def to_json(self) -> str:
        return json.dumps({
            "documents": [
                {
                    "document":                 doc.document,
                    "document_name":            doc.document_name,
                    "signature_format":         doc.signature_format,
                    "conformance_level":        doc.conformance_level,
                    "signed_props":             doc.signed_props,
                    "signed_envelope_property": doc.signed_envelope_property,
                    "container":                doc.container,
                }
                for doc in self.documents
            ],
            "endEntityCertificate": self.end_entity_certificate,
            "certificateChain":     self.certificate_chain,
            "hashAlgorithmOID":     self.hash_algorithm_oid,
        })

class CalculateHashResponse:
    hashes: list[str]
    signature_date: int

    def __init__(
        self,
        hashes: list[str],
        signature_date: int,
    ):
        if not hashes:
            raise ValueError("Hashes list cannot be empty")
        if not signature_date:
            raise ValueError("Signature date cannot be empty")

        self.hashes = hashes
        self.signature_date = signature_date

    @classmethod
    def from_json(cls, data: dict) -> "CalculateHashResponse":
        return cls(
            hashes=data["hashes"],
            signature_date=data["signature_date"],
        )

class ObtainSignedDocumentRequest:
    documents: list[DocumentsSignDocRequest]
    hash_algorithm_oid: str
    return_validation_info: bool
    end_entity_certificate: str
    certificate_chain: list[str]
    date: int
    signatures: list[str]

    def __init__(
        self,
        documents: list[DocumentsSignDocRequest],
        hash_algorithm_oid: str,
        end_entity_certificate: str,
        date: int,
        signatures: list[str],
        certificate_chain: Optional[list[str]] = None,
        return_validation_info: bool = False,
    ):
        if not documents:
            raise ValueError("At least one document must be present in the request")
        if not hash_algorithm_oid:
            raise ValueError("The hashAlgorithmOID must be present")
        if not end_entity_certificate:
            raise ValueError("The certificate must be present")
        if not date:
            raise ValueError("The 'date' value must be present")
        if not signatures:
            raise ValueError("The list of signatures must be present")

        self.documents = documents
        self.hash_algorithm_oid = hash_algorithm_oid
        self.return_validation_info = return_validation_info
        self.end_entity_certificate = end_entity_certificate
        self.certificate_chain = certificate_chain or []
        self.date = date
        self.signatures = signatures

    def to_json(self) -> str:
        return json.dumps({
            "documents": [
                {
                    "document":                 doc.document,
                    "document_name":            doc.document_name,
                    "signature_format":         doc.signature_format,
                    "conformance_level":        doc.conformance_level,
                    "signed_props":             doc.signed_props,
                    "signed_envelope_property": doc.signed_envelope_property,
                    "container":                doc.container,
                }
                for doc in self.documents
            ],
            "hashAlgorithmOID":       self.hash_algorithm_oid,
            "returnValidationInfo":   self.return_validation_info,
            "endEntityCertificate":   self.end_entity_certificate,
            "certificateChain":       self.certificate_chain,
            "date":                   self.date,
            "signatures":             self.signatures,
        })

class ObtainSignedDocumentResponse:
    document_with_signature: list[str]
    signature_object: list[str]
    response_id: Optional[str]
    validation_info: Optional[str]

    def __init__(
        self,
        document_with_signature: list[str],
        signature_object: list[str],
        response_id: Optional[str],
        validation_info: Optional[str] = None,
    ):
        if not document_with_signature and not signature_object:
            raise ValueError("At least one document with signature or signature object must be present")

        self.document_with_signature = document_with_signature
        self.signature_object = signature_object
        self.response_id = response_id
        self.validation_info = validation_info

    @classmethod
    def from_json(cls, data: dict) -> "ObtainSignedDocumentResponse":
        return cls(
            document_with_signature=data["documentWithSignature"],
            signature_object=data["signatureObject"],
            response_id=data.get("responseID"),
        )