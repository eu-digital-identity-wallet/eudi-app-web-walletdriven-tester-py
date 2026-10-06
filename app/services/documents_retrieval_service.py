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

import requests, re
from typing import Tuple
from flask import current_app as app
from app.schemas.document_retrieval import DocumentRetrievalRequestObject, DocumentRetrievalResponse, DocumentRetrievalRequest

def get_request_object_through_document_retrieval(request: DocumentRetrievalRequest) -> DocumentRetrievalRequestObject:
    request_uri = request.request_uri
    client_id = request.client_id

    response = requests.get(request_uri)
    if response.status_code == 200:
        request_object = DocumentRetrievalRequestObject.from_jwt(response.text)
        app.logger.info(f"Retrieved the Request Object with document to sign from Relying Party.")
        return request_object
    else:
        error = response.json()["error"]
        message = response.json()["message"]
        app.logger.error(f"It was impossible to retrieve Request Object from Relying Party: {error} - {message}")
        raise ValueError(f"It was impossible to retrieve Request Object from Relying Party: {error} - {message}")

def post_signed_document_response_uri(response_uri: str, signed_documents: list[str], packagings: list[str]) -> str:
    signature_objects = []
    documents_with_signature = []
    for doc, packaging in zip(signed_documents, packagings):
        if packaging == "DETACHED":
            signature_objects.append(doc)
        else:
            documents_with_signature.append(doc)
    payload = DocumentRetrievalResponse(documentWithSignature=documents_with_signature, signatureObject = signature_objects)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # encoded_payload = urlencode(payload)
    response = requests.post(url=response_uri, data=payload.to_dict(), headers=headers)
    if response.status_code == 200:
        app.logger.info(f"Uploaded signed document to Relying Party {response_uri}")
        return response.text
    else:
        app.logger.error(f"It was impossible to upload signed document to Relying Party: {response.text}")
        raise ValueError(f"It was impossible to upload signed document to Relying Party: {response.text}")

def get_document_from_uri(document_uri: str) -> Tuple[bytes, str]:
    match = re.search(r'/document/([^/]+)$', document_uri)
    if not match:
        raise ValueError("Invalid URI: Unable to extract filename")
    filename = match.group(1)

    document = requests.get(document_uri, stream=True)

    if document.status_code != 200:
        raise ValueError(f"Failed to get document from URI: {document.text}")

    return document.content, filename