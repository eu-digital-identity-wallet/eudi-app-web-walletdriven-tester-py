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
from flask import Blueprint, render_template, request, make_response, redirect, url_for
from urllib.parse import urlparse, parse_qsl

from app.models.session_state import SessionState
from app.services import oauth2_api_client as oauth2service
from app.utils.pkce import setup_pkce_session
from app.utils.session import update_session_values, get_session_value, remove_session_values
from app.core.config import settings

auth_routes = Blueprint("auth", __name__, url_prefix="/tester/auth")
auth_routes.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@auth_routes.route('/preview', methods=['POST'])
def preview_authorization_request():
    scope = request.json["scope"]
    if scope not in ["service", "credential", "credential-creation", "credential-deletion"]:
        raise ValueError("Invalid scope provided")
    authentication_flow = request.json["authenticationFlow"]
    if authentication_flow not in ["same", "cross", "form"]:
        raise ValueError("Invalid authentication flow provided")

    update_session_values(SessionState.OAUTH_AUTHENTICATION_FLOW, authentication_flow)

    code_challenge = get_session_value(SessionState.CODE_CHALLENGE)
    if code_challenge is None:
        _, code_challenge = setup_pkce_session()

    if scope == "credential-creation":
        oauth_request = f"GET {oauth2service.get_oauth2_authorize_request_preview(scope="credential-creation", code_challenge=code_challenge, authentication=authentication_flow)}"
        redirect_url = url_for("auth.create_certificate_authentication")
    elif scope == "service":
        oauth_request = f"GET {oauth2service.get_oauth2_authorize_request_preview(scope="service", code_challenge=code_challenge, authentication=authentication_flow)}"
        redirect_url = url_for("auth.service_authentication")
    elif scope == "credential":
        hashes = get_session_value(SessionState.HASHES)
        credential_id = get_session_value(SessionState.CERTIFICATE_ID)
        hash_algorithm_oid = get_session_value(SessionState.DIGEST_ALGORITHM_OID)
        oauth_request = f"GET {oauth2service.get_oauth2_authorize_request_preview(
            scope="credential",
            authentication=authentication_flow,
            code_challenge=code_challenge,
            credential_id=credential_id,
            numSignatures=len(hashes),
            hashAlgorithmOID=hash_algorithm_oid,
            hashes=hashes
        )}"
        redirect_url = url_for("auth.credential_authentication")
    elif scope == "credential-deletion":
        credential_id = request.json["credentialId"]
        update_session_values(SessionState.CERTIFICATE_ID, credential_id)
        oauth_request = f"GET {oauth2service.get_oauth2_authorize_request_preview(scope="credential-deletion", authentication=authentication_flow,
            code_challenge=code_challenge, credential_id=credential_id)}"
        redirect_url = url_for("auth.delete_certificate_authentication")
    return {"requestUrl": oauth_request, "redirectUrl": redirect_url}

def _oauth_helper(scope: str, oauth_call, extra_args_fn=None):
    remove_session_values(SessionState.JSESSIONID)
    code_challenge = get_session_value(SessionState.CODE_CHALLENGE)
    authentication = get_session_value(SessionState.OAUTH_AUTHENTICATION_FLOW)
    update_session_values(SessionState.OAUTH_SCOPE, scope)
    extra_args = extra_args_fn() if extra_args_fn else ()
    location, jsessionid = oauth_call(code_challenge, authentication, *extra_args)
    update_session_values(SessionState.JSESSIONID, jsessionid)
    update_session_values(SessionState.FORM_LOGIN_LOCATION, location)

    if authentication == "cross":
        return redirect(location)
    elif authentication == "form":
        return make_response(render_template("oauth-auth-server-authentication.html",
                                             test_form_auth=True, location=location,
                                             username=settings.OAUTH_USERNAME, password=settings.OAUTH_PASSWORD))
    else:
        return make_response(render_template("oauth-auth-server-authentication.html",
                                             test_form_auth=False, location=location))

@auth_routes.route('/service', methods=['GET'])
def service_authentication():
    return _oauth_helper(
        scope = "service",
        oauth_call=oauth2service.oauth2_authorize_service,
    )

@auth_routes.route('/create', methods=['GET'])
def create_certificate_authentication():
    return _oauth_helper(
        scope="credential-creation",
        oauth_call=oauth2service.oauth2_authorize_credential_create
    )

@auth_routes.route('/delete', methods=['GET'])
def delete_certificate_authentication():
    return _oauth_helper(
        scope="credential-deletion",
        oauth_call=oauth2service.oauth2_authorize_credential_delete,
        extra_args_fn=lambda: (
            get_session_value(SessionState.CERTIFICATE_ID),
        )
    )

@auth_routes.route('/credential', methods=['GET'])
def credential_authentication():
    return _oauth_helper(
        scope="credential",
        oauth_call=oauth2service.oauth2_authorize_credential,
        extra_args_fn=lambda: (
            get_session_value(SessionState.HASHES),
            get_session_value(SessionState.CERTIFICATE_ID),
            len(get_session_value(SessionState.HASHES)),
            get_session_value(SessionState.DIGEST_ALGORITHM_OID)
        )
    )

@auth_routes.route('/login', methods=['POST'])
def login():
    jsessionid = get_session_value(SessionState.JSESSIONID)
    location = get_session_value(SessionState.FORM_LOGIN_LOCATION)
    new_location, new_jsessionid = oauth2service.oauth2_form_login(location, settings.OAUTH_USERNAME, settings.OAUTH_PASSWORD, jsessionid)
    update_session_values(SessionState.JSESSIONID, new_jsessionid)
    parsed = urlparse(new_location)
    query_params = dict(parse_qsl(parsed.query))
    location = oauth2service.oauth2_authorize_with_given_parameters(new_jsessionid, query_params)
    return redirect(location)

