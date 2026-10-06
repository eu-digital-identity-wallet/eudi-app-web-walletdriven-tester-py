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

import os
from flask import Blueprint, request, current_app as app, url_for, redirect
from app.services import documents_retrieval_service
from app.models.session_state import SessionState
from app.schemas.document_retrieval import DocumentRetrievalRequest
from app.utils.session import update_session_values, clear_session

relying_party_routes = Blueprint("rp_routes", __name__, url_prefix="/tester/relying_party_service")
relying_party_routes.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@relying_party_routes.route("/", methods=["GET"])
def get_document_retrieval_signing_request():
    app.logger.info("Received a signing request from a relying party.")
    doc_retrieval_request = DocumentRetrievalRequest(request.args)
    request_object = documents_retrieval_service.get_request_object_through_document_retrieval(doc_retrieval_request)
    clear_session()
    update_session_values(SessionState.DOCUMENT_ORIGIN, "relying_party")
    update_session_values(SessionState.RESPONSE_URI, request_object.response_uri)
    update_session_values(SessionState.HASH_ALGORITHM_OID, request_object.hash_algorithm_oid)
    update_session_values(SessionState.DOCUMENT_LOCATIONS, request_object.document_locations)
    return redirect(url_for("index.get_tester_home_page"))