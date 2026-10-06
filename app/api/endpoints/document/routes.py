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

import mimetypes
import os, json
from flask import Blueprint, request, render_template, jsonify, current_app as app
from app.core.config import settings
from app.services import sca_service, documents_manage_service, documents_retrieval_service, csc_api_client
from app.models.session_state import SessionState
from app.utils.session import update_session_values, remove_session_values, get_session_value

documents_routes = Blueprint("documents_routes", __name__, url_prefix="/tester/document")
documents_routes.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

def _resolve_hash_algos(algo_oid: str | None) -> list:
    if algo_oid is not None:
        return [{"name": settings.SUPPORTED_DIGEST_ALGOS.get(algo_oid), "oid": algo_oid}]

    hash_algos = []
    for hash_algo_oid, hash_algo_name in settings.SUPPORTED_DIGEST_ALGOS.items():
        hash_algos.append({"name": hash_algo_name, "oid": hash_algo_oid})
    return hash_algos

@documents_routes.route('/select', methods=['GET'])
def get_document_select_page():
    predefined_files = None
    if get_session_value(SessionState.DOCUMENT_ORIGIN) == "relying_party":
        document_locations = get_session_value(SessionState.DOCUMENT_LOCATIONS)
        predefined_files = []
        received_documents_info = []
        for loc in document_locations:
            document, filename = documents_retrieval_service.get_document_from_uri(loc.uri)
            saved_file_path, saved_filename = documents_manage_service.save_document_with_name(document, filename)
            data = documents_manage_service.get_base64_document(saved_file_path)
            mimetype, _ = mimetypes.guess_type(saved_filename)
            predefined_files.append({"name": saved_filename, "data": data, "type": mimetype})
            received_documents_info.append({"filepath": saved_file_path, "filename": saved_filename})
        update_session_values(SessionState.RECEIVED_DOCUMENTS, received_documents_info)
        hash_algos = _resolve_hash_algos(get_session_value(SessionState.HASH_ALGORITHM_OID))
    else:
        hash_algos = _resolve_hash_algos(None)

    remove_session_values(SessionState.DOCUMENTS)
    return render_template('document-select.html', digest_algorithms=hash_algos, received_files=predefined_files)

def _resolve_filepaths_and_names(predefined_files: list | None, uploaded_files=None) -> tuple[list, list]:
    filepaths, filenames = [], []
    if predefined_files is not None:
        app.logger.info("Retrieving paths and names from predefined files")
        for f in predefined_files:
            filepaths.append(f["filepath"])
            filenames.append(f["filename"])
        app.logger.info("Retrieved paths and names from predefined files")
    else:
        app.logger.info("Retrieving paths and names from request")
        for f in (uploaded_files or []):
            file_path, filename = documents_manage_service.save_document(f)
            filepaths.append(file_path)
            filenames.append(filename)
        app.logger.info("Retrieved paths and names from request")
    return filepaths, filenames

@documents_routes.route("/select", methods=["POST"])
def post_documents_selected_signature_options():
    app.logger.info("Received documents to sign and signing options")
    options = request.form.getlist("options")
    predefined_files = get_session_value(SessionState.RECEIVED_DOCUMENTS)
    filepaths, filenames = _resolve_filepaths_and_names(predefined_files, request.files.getlist("files"))
    app.logger.info("Retrieved files' names and paths")
    documents_signature_option = [
        {
            "filepath": path,
            "filename": name,
            "container": option["container"],
            "signature_format": option["signature_format"],
            "packaging": option["packaging"],
            "level": option["level"]
        }
        for path, name, option_json in zip(filepaths, filenames, options)
        for option in [json.loads(option_json)]
    ]
    update_session_values(SessionState.DOCUMENTS, documents_signature_option)
    update_session_values(SessionState.DIGEST_ALGORITHM_OID, request.form.get("digest_algorithm"))

    remove_session_values(SessionState.RECEIVED_DOCUMENTS)
    return jsonify({"status": "ok"}), 200


def _prepare_hashes(signing_options: list, hash_algorithm_oid: str):
    documents = documents_manage_service.get_documents_content_from_filepath(signing_options)
    try:
        preview_url, preview_body = sca_service.get_calculate_hash_preview(
            documents=documents,
            signing_options=signing_options,
            end_entity_certificate=get_session_value(SessionState.END_ENTITY_CERTIFICATE),
            certificate_chain=[get_session_value(SessionState.CERTIFICATE_CHAIN)],
            hash_algorithm_oid=hash_algorithm_oid
        )

        calculate_hash_response = sca_service.calculate_hash(
            documents = documents,
            signing_options = signing_options,
            end_entity_certificate = get_session_value(SessionState.END_ENTITY_CERTIFICATE),
            certificate_chain = [get_session_value(SessionState.CERTIFICATE_CHAIN)],
            hash_algorithm_oid = hash_algorithm_oid
        )
        update_session_values(SessionState.HASHES, calculate_hash_response.hashes)
        update_session_values(SessionState.SIGNATURE_DATE, calculate_hash_response.signature_date)

        return preview_url, preview_body
    except ValueError as e:
        app.logger.error("Failed to retrieve the hashes and signature date from the signature creation application.")
        raise e

@documents_routes.route("/hash", methods=["GET"])
def get_document_hash_page():
    test_form_supported = "test-form" in settings.OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS
    cross_device_flow_supported = "cross-device" in settings.OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS
    signing_options = get_session_value(SessionState.DOCUMENTS)
    hash_algorithm_oid = get_session_value(SessionState.DIGEST_ALGORITHM_OID)
    preview_url, preview_body = _prepare_hashes(signing_options, hash_algorithm_oid)
    json_body = json.loads(preview_body)
    return render_template('document-hash.html', hash_create_url=f"POST {preview_url}",
                           hash_create_body=json_body, requires_credential_id = False,
                           cross_device_flow_supported=cross_device_flow_supported, test_form_supported=test_form_supported)

def _sign_document(signing_options, hashes, credential_access_token, credential_id, hash_algorithm_oid, sign_algorithm_oid):
    app.logger.info("Signing %d files with %d hashes", len(signing_options), len(hashes))
    signHash_url, signHash_request = csc_api_client.preview_csc_req("signatures_signhash", hashes=hashes, credential_id=credential_id, sign_algo=sign_algorithm_oid, hash_algorithm_oid=hash_algorithm_oid)
    response = csc_api_client.post_csc_v2_signatures_signhash(credential_access_token, credential_id, hashes, sign_algorithm_oid, hash_algorithm_oid)
    documents = [documents_manage_service.get_base64_document(d["filepath"]) for d in signing_options]

    try:
        obtain_signed_doc_url, obtain_signed_doc_body = sca_service.get_obtain_signed_doc_preview(
            documents=documents, signing_options=signing_options,
            end_entity_certificate=get_session_value(SessionState.END_ENTITY_CERTIFICATE),
            certificate_chain=[get_session_value(SessionState.CERTIFICATE_CHAIN)],
            hash_algorithm_oid=hash_algorithm_oid, signatures=response.signatures,
            date=get_session_value(SessionState.SIGNATURE_DATE)
        )

        signed_documents = sca_service.obtain_signed_doc(
            documents=documents, signing_options=signing_options,
            end_entity_certificate=get_session_value(SessionState.END_ENTITY_CERTIFICATE),
            certificate_chain=[get_session_value(SessionState.CERTIFICATE_CHAIN)],
            hash_algorithm_oid=hash_algorithm_oid, signatures=response.signatures,
            date=get_session_value(SessionState.SIGNATURE_DATE))
        app.logger.info("Received %d signed documents", len(signed_documents.document_with_signature))
        return signed_documents, signHash_url, signHash_request, obtain_signed_doc_url, obtain_signed_doc_body
    except ValueError as e:
        app.logger.error("Failed to retrieve the signed documents from the signature creation application.")
        raise e

@documents_routes.route('/sign', methods=['GET'])
def get_document_signed_page():
    signing_options         = get_session_value(SessionState.DOCUMENTS)
    hashes                  = get_session_value(SessionState.HASHES)
    credential_access_token = get_session_value(SessionState.CREDENTIAL_ACCESS_TOKEN)
    credential_id           = get_session_value(SessionState.CERTIFICATE_ID)
    digest_algorithm_oid    = get_session_value(SessionState.DIGEST_ALGORITHM_OID)
    sign_algorithm_oid      = get_session_value(SessionState.KEY_ALGOS)
    sign_algorithm_oid      = sign_algorithm_oid[0] if isinstance(sign_algorithm_oid, list) else sign_algorithm_oid #"1.2.840.10045.2.1"

    signed_documents, signHash_url, signHash_request, obtain_signed_doc_url, obtain_signed_doc_body =\
        _sign_document(signing_options, hashes, credential_access_token, credential_id, digest_algorithm_oid, sign_algorithm_oid)

    remove_session_values(SessionState.DOCUMENTS)
    remove_session_values(SessionState.CERTIFICATE_ID)
    remove_session_values(SessionState.END_ENTITY_CERTIFICATE)
    remove_session_values(SessionState.CERTIFICATE_CHAIN)
    remove_session_values(SessionState.HASHES)
    remove_session_values(SessionState.SIGNATURE_DATE)
    remove_session_values(SessionState.CREDENTIAL_ACCESS_TOKEN)

    signed_doc = None
    if get_session_value(SessionState.DOCUMENT_LOCATIONS):
        document_retrieval = True
        signed_envelope_property_list = []
        for d in signing_options:
            os.remove(d["filepath"])
            signed_envelope_property_list.append(d["packaging"])
        response_uri = get_session_value(SessionState.RESPONSE_URI)
        _ = documents_retrieval_service.post_signed_document_response_uri(response_uri, signed_documents.document_with_signature, signed_envelope_property_list)
        remove_session_values(SessionState.DOCUMENT_LOCATIONS)
        remove_session_values(SessionState.RESPONSE_URI)
    else:
        document_retrieval = False
        mime_types, new_filenames = [], []

        for d in signing_options:
            mime_type, new_name = documents_manage_service.get_mime_type_and_filename(d)
            mime_types.append(mime_type)
            new_filenames.append(new_name)
            os.remove(d["filepath"])
        signed_doc = list(zip(mime_types, signed_documents.document_with_signature, new_filenames))

    json_sign_hash_body = json.loads(signHash_request)
    json_get_signed_doc_body = json.loads(obtain_signed_doc_body)

    return render_template('document-signed.html', redirect_url=settings.SERVICE_URL,
                           signed_doc=signed_doc, document_retrieval=document_retrieval,
                           signHash_url=signHash_url, signHash_request=json_sign_hash_body,
                           obtain_signed_doc_url=obtain_signed_doc_url, obtain_signed_doc_body=json_get_signed_doc_body)