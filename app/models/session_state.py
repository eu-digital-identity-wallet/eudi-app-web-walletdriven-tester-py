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

class SessionState:
    # OAuth2 Values
    CODE_VERIFIER = "code_verifier"
    CODE_CHALLENGE = "code_challenge"
    OAUTH_STATE = "state"
    OAUTH_SCOPE = "scope"
    OAUTH_AUTHENTICATION_FLOW = "authentication_flow"

    # Authentication Values
    CREDENTIAL_LIST_ACCESS_TOKEN = "service_access_token"
    DELETE_CREDENTIAL_ACCESS_TOKEN = "delete_credential_access_token"
    CREDENTIAL_ACCESS_TOKEN = "credential_access_token"
    JSESSIONID = "JSESSIONID"
    FORM_LOGIN_LOCATION = "form_login_location"

    # Document Selection Values
    DOCUMENTS = "documents"
    DIGEST_ALGORITHM_OID = "digest_algorithm"

    # Certificate Values
    LIST_CERTIFICATE_ID = "list_certificate_id"
    CERTIFICATE_ID = "credential_id"
    END_ENTITY_CERTIFICATE = "end_entity_certificate"
    CERTIFICATE_CHAIN = "certificate_chain"
    KEY_ALGOS = "key_algos"

    # SCA Response Values
    HASHES = "hashes"
    SIGNATURE_DATE = "signature_date"

    # Document Retrieval Values
    DOCUMENT_ORIGIN = "document_origin"
    RESPONSE_URI = "response_uri"
    HASH_ALGORITHM_OID = "hash_algorithm_oid"
    DOCUMENT_LOCATIONS = "document_locations"
    RECEIVED_DOCUMENTS = "received_documents"