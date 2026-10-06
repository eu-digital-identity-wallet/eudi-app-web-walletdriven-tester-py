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

import requests
from flask import current_app as app
from requests import Request

from app.core.config import settings
from app.schemas.sca import DocumentsSignDocRequest, CalculateHashRequest, CalculateHashResponse, ObtainSignedDocumentRequest, \
    ObtainSignedDocumentResponse

calculate_hash_endpoint = "/signatures/calculate_hash"
obtain_signed_doc_endpoint = "/signatures/obtain_signed_doc"

def _get_documents_for_request(documents: list, signing_options: list) -> list[DocumentsSignDocRequest]:
    documents_for_request = []
    for document, options in zip(documents, signing_options):
        documents_for_request.append(
            DocumentsSignDocRequest(document, options["filename"], options["signature_format"], options["level"], None,
                                    options["packaging"], options["container"]))
    return documents_for_request

def get_calculate_hash_preview(documents: list, signing_options: list, end_entity_certificate: str,
                               certificate_chain: list, hash_algorithm_oid: str) -> tuple[str, str]:
    calculate_hash_url = settings.SCA_URL + calculate_hash_endpoint
    documents_for_request = _get_documents_for_request(documents, signing_options)
    calculate_hash_request = CalculateHashRequest(
        documents_for_request,
        end_entity_certificate,
        hash_algorithm_oid,
        certificate_chain
    )
    headers = {
        'Content-Type': 'application/json'
    }
    req = Request(method="POST", url=calculate_hash_url, headers=headers, data=calculate_hash_request.to_json()).prepare()
    return req.url, req.body

def calculate_hash(documents: list, signing_options: list, end_entity_certificate: str, certificate_chain: list,
                           hash_algorithm_oid: str) -> CalculateHashResponse:
    calculate_hash_url = settings.SCA_URL + calculate_hash_endpoint

    documents_for_request = _get_documents_for_request(documents, signing_options)
    calculate_hash_request = CalculateHashRequest(
        documents_for_request,
        end_entity_certificate,
        hash_algorithm_oid,
        certificate_chain
    )

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(calculate_hash_url , headers=headers, data=calculate_hash_request.to_json())

    if response.status_code == 200:
        calculate_hash_response = CalculateHashResponse.from_json(response.json())
        app.logger.info(f"Retrieved hashes and signature date from signature creation application ({settings.SCA_URL})")
        return calculate_hash_response
    else:
        error = response.json()["error"]
        message = response.json()["message"]
        app.logger.error(f"It was impossible to retrieve hashes and signature date from signature creation application: {error} - {message}")
        raise ValueError(f"It was impossible to retrieve hashes and signature date from signature creation application: {error} - {message}")

def get_obtain_signed_doc_preview(documents: list, signing_options: list, end_entity_certificate: str, certificate_chain: list,
                           hash_algorithm_oid: str, signatures: list, date: int) -> tuple[str, str]:
    obtain_signed_doc_url = settings.SCA_URL + obtain_signed_doc_endpoint

    documents_for_request = _get_documents_for_request(documents, signing_options)
    obtain_signed_doc_request = ObtainSignedDocumentRequest(
        documents=documents_for_request,
        hash_algorithm_oid=hash_algorithm_oid,
        end_entity_certificate=end_entity_certificate,
        date=date,
        signatures=signatures,
        certificate_chain=certificate_chain
    )

    headers = {
        'Content-Type': 'application/json'
    }
    req = Request(method="POST", url=obtain_signed_doc_url, headers=headers, data=obtain_signed_doc_request.to_json()).prepare()
    return req.url, req.body

def obtain_signed_doc(documents: list, signing_options: list, end_entity_certificate: str, certificate_chain: list,
                           hash_algorithm_oid: str, signatures: list, date: int) -> ObtainSignedDocumentResponse:
    obtain_signed_doc_url = settings.SCA_URL + obtain_signed_doc_endpoint

    documents_for_request = _get_documents_for_request(documents, signing_options)
    obtain_signed_doc_request = ObtainSignedDocumentRequest(
        documents=documents_for_request,
        hash_algorithm_oid=hash_algorithm_oid,
        end_entity_certificate=end_entity_certificate,
        date=date,
        signatures=signatures,
        certificate_chain=certificate_chain
    )

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(obtain_signed_doc_url, headers=headers, data=obtain_signed_doc_request.to_json())
    if response.status_code == 200:
        signed_doc = ObtainSignedDocumentResponse.from_json(response.json())
        app.logger.info(f"Retrieved signed documents from signature creation application ({settings.SCA_URL})")
        return signed_doc
    else:
        error = response.json()["error"]
        message = response.json()["message"]
        app.logger.error(f"It was impossible to retrieve signed documents from signature creation application: {error} - {message}")
        raise ValueError(f"It was impossible to retrieve signed documents from signature creation application: {error} - {message}")

