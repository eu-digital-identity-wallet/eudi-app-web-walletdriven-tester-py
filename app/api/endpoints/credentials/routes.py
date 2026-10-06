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
import os
from flask import Blueprint, render_template, request, redirect, url_for

from app.core.config import Settings
from app.models.session_state import SessionState
from app.services import csc_api_client
from app.utils.session import update_session_values, get_session_value

credentials_routes = Blueprint("credentials", __name__, url_prefix="/tester/credentials")
credentials_routes.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@credentials_routes.route("/retrieve", methods=["GET"])
def get_credentials_retrieve_options():
    test_form_supported = "test-form" in Settings.OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS
    cross_device_flow_supported = "cross-device" in Settings.OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS
    return render_template('certificate-retrieve.html', requires_credential_id = False,
                           cross_device_flow_supported=cross_device_flow_supported, test_form_supported=test_form_supported)

@credentials_routes.route("/create/preview", methods=["GET"])
def create_credentials_preview():
    url, create_certificate_body = csc_api_client.preview_csc_req( "credential_create")
    return render_template('certificate-create.html',
                           create_credential_url=url,
                           create_credential_body=json.loads(create_certificate_body))

@credentials_routes.route("/create", methods=["GET"])
def create_credentials():
    access_token = get_session_value(SessionState.CREDENTIAL_LIST_ACCESS_TOKEN)
    csc_api_client.post_csc_v2_credentials_create(access_token)
    return redirect(url_for("credentials.list_credentials"))

@credentials_routes.route("/list", methods=["GET"])
def list_credentials():
    access_token = get_session_value(SessionState.CREDENTIAL_LIST_ACCESS_TOKEN)
    credential_list_url, credential_list_body = csc_api_client.preview_csc_req("credential_list")
    response = csc_api_client.post_csc_credential_list(access_token)
    update_session_values(SessionState.LIST_CERTIFICATE_ID, response.credential_ids)
    json_body = json.loads(credential_list_body)
    return render_template('certificate-list.html', credential_list_url=f"POST {credential_list_url}",
                           credential_list_body=json_body, list_credentials_ids=response.credential_ids)

@credentials_routes.route("/select", methods=["POST"])
def select_credential():
    credential_id = request.get_json().get("credentialID")
    update_session_values(SessionState.CERTIFICATE_ID, credential_id)

    access_token = get_session_value(SessionState.CREDENTIAL_LIST_ACCESS_TOKEN)
    certificates, key_algos = csc_api_client.post_csc_v2_credentials_info(access_token, credential_id)

    update_session_values(SessionState.END_ENTITY_CERTIFICATE, certificates[0])
    update_session_values(SessionState.CERTIFICATE_CHAIN, certificates[1])
    update_session_values(SessionState.KEY_ALGOS, key_algos)
    return "success", 200

@credentials_routes.route("/delete/preview", methods=["GET"])
def delete_credentials_preview():
    test_form_supported = "test-form" in Settings.OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS
    cross_device_flow_supported = "cross-device" in Settings.OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS
    list_credentials_ids = get_session_value(SessionState.LIST_CERTIFICATE_ID)
    return render_template('certificate-delete.html', list_credentials_ids=list_credentials_ids,
                           requires_credential_id = True, cross_device_flow_supported=cross_device_flow_supported,
                           test_form_supported=test_form_supported)


@credentials_routes.route("/delete", methods=["GET"])
def delete_credentials():
    access_token = get_session_value(SessionState.DELETE_CREDENTIAL_ACCESS_TOKEN)
    credential_id = get_session_value(SessionState.CERTIFICATE_ID)
    url, delete_certificate = csc_api_client.preview_csc_req("credential_delete", credential_id=credential_id)
    csc_api_client.post_csc_v2_credentials_delete(access_token, credential_id)
    json_body = json.loads(delete_certificate)
    return render_template("certificate-delete-confirm.html", delete_request_url=url, delete_request_body=json_body)
