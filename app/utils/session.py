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

from flask import session
from app.models.session_state import SessionState

_VALID_KEYS = {
    value for key, value in vars(SessionState).items()
    if not key.startswith("_")
}

def _validate_key(key: str) -> None:
    if key not in _VALID_KEYS:
        raise KeyError(f"'{key}' is not a valid session key.")

def update_session_values(key: str, value):
    _validate_key(key)
    session[key] = value

def remove_session_values(key):
    _validate_key(key)
    session.pop(key, None)

def get_session_value(key: str):
    _validate_key(key)
    return session.get(key)


def clear_session() -> None:
    for key in _VALID_KEYS:
        session.pop(key, None)

def clear_session_ignore_document_retrieval() -> None:
    for key in _VALID_KEYS:
        if not (key in [SessionState.DOCUMENT_ORIGIN, SessionState.RESPONSE_URI,
        SessionState.HASH_ALGORITHM_OID, SessionState.DOCUMENT_LOCATIONS]):
            session.pop(key, None)