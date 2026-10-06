# coding: latin-1
###############################################################################
# Copyright (c) 2023 European Commission
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
from app.utils.session import clear_session_ignore_document_retrieval
from app.schemas.csc.oauth2 import OAuth2CallbackRequest
from app.services import oauth2_api_client as oauth2service
from flask import Blueprint, render_template, request, redirect, url_for, current_app as app, session
from app.utils.session import update_session_values, remove_session_values, get_session_value
from app.core.config import settings
from app.models.session_state import SessionState


base_routes = Blueprint("index", __name__, url_prefix="/")
base_routes.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@base_routes.route('/', methods=['GET'])
def get_tester_landing_page():
    return render_template('landing.html', redirect_url=settings.SERVICE_URL, rp_url=settings.RP_URL)

@base_routes.route('/tester', methods=['GET'])
def get_tester_home_page():
    is_rp_request = get_session_value(SessionState.DOCUMENT_ORIGIN) == "relying_party"
    clear_session_ignore_document_retrieval()
    return render_template('home.html', is_rp_request=is_rp_request)

def _clean_session_oauth2_variables():
    remove_session_values(SessionState.JSESSIONID)
    remove_session_values(SessionState.OAUTH_SCOPE)
    remove_session_values(SessionState.CODE_CHALLENGE)
    remove_session_values(SessionState.CODE_VERIFIER)

def _handle_token_by_scope(scope: str, code: str):
    authentication = get_session_value(SessionState.OAUTH_AUTHENTICATION_FLOW)
    if scope == "service":
        response = oauth2service.oauth2_token(
            code_verifier=get_session_value(SessionState.CODE_VERIFIER),
            code=code,
            authentication=authentication
        )
        _clean_session_oauth2_variables()
        update_session_values(SessionState.CREDENTIAL_LIST_ACCESS_TOKEN, response.access_token)
        return redirect(url_for("credentials.list_credentials"))

    elif scope == "credential-creation":
        response = oauth2service.oauth2_token_credential_create(
            code_verifier=get_session_value(SessionState.CODE_VERIFIER),
            code=code,
            authentication=authentication
        )
        _clean_session_oauth2_variables()
        update_session_values(SessionState.CREDENTIAL_LIST_ACCESS_TOKEN, response.access_token)
        return redirect(url_for("credentials.create_credentials_preview"))

    elif scope == "credential":
        response = oauth2service.oauth2_token(
            code_verifier=get_session_value(SessionState.CODE_VERIFIER),
            code=code,
            authentication=authentication
        )
        _clean_session_oauth2_variables()
        update_session_values(SessionState.CREDENTIAL_ACCESS_TOKEN, response.access_token)
        return redirect(url_for("documents_routes.get_document_signed_page"))

    elif scope == "credential-deletion":
        response = oauth2service.oauth2_token_credential_delete(
            code_verifier=get_session_value(SessionState.CODE_VERIFIER),
            code=code,
            credential_id=get_session_value(SessionState.CERTIFICATE_ID),
            authentication=authentication
        )
        _clean_session_oauth2_variables()
        update_session_values(SessionState.DELETE_CREDENTIAL_ACCESS_TOKEN, response.access_token)
        return redirect(url_for("credentials.delete_credentials"))

    app.logger.error("Unknown scope received: %s", scope)
    return render_template("500.html", error=f"Unknown scope: {scope}"), 500

@base_routes.route("/tester/oauth2/callback", methods=["GET"])
@base_routes.route("/tester/oauth/login/code", methods=["GET"])
def oauth_authorize_callback_endpoint():
    params = OAuth2CallbackRequest(request.args)
    scope = get_session_value(SessionState.OAUTH_SCOPE)

    try:
        oauth2service.validate_callback(params, get_session_value(SessionState.CODE_VERIFIER), session.sid)
        app.logger.info("Received request with code: %s and state: %s", params.code, params.state)
    except ValueError as e:
       app.logger.error("Invalid OAuth callback params: %s", e)
       return render_template("500.html", error=str(e)), 500

    return _handle_token_by_scope(scope, params.code)