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
import base64, hashlib, secrets

from app.core.config import settings
from app.models.session_state import SessionState
from app.utils.session import remove_session_values, update_session_values

def _get_pkce_code_verifier_and_challenge():
    code_verifier = secrets.token_urlsafe(32)
    if settings.OAUTH_CODE_CHALLENGE_METHOD == "S256":
        code_challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).rstrip(b'=').decode()
        return code_verifier, code_challenge
    else: #plain
        return code_verifier, code_verifier

def setup_pkce_session():
    remove_session_values(SessionState.CODE_VERIFIER)
    remove_session_values(SessionState.CODE_CHALLENGE)
    code_verifier, code_challenge = _get_pkce_code_verifier_and_challenge()
    update_session_values(SessionState.CODE_VERIFIER, code_verifier)
    update_session_values(SessionState.CODE_CHALLENGE, code_challenge)
    return code_verifier, code_challenge