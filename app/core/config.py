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
from typing import Optional

"""
This config.py contains configuration data.
"""
class Settings:
    ENV: str = os.getenv("ENV", "dev")

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    SESSION_TYPE: str = "filesystem"
    SESSION_FILE_THRESHOLD: int = 100
    SESSION_PERMANENT: bool = False
    SESSION_USE_SIGNER: bool = True
    SESSION_KEY_PREFIX: str = "wallet-centric-session:"
    SESSION_COOKIE_NAME: str = "wallet-tester-session"
    SESSION_COOKIE_SAMESITE: Optional[str] = None
    SESSION_COOKIE_SECURE: bool = True

    DOCUMENTS_UPLOAD_FOLDER: str = os.getenv("DOCUMENTS_UPLOAD_FOLDER")

    SERVICE_URL: str = os.getenv("SERVICE_URL")
    RP_URL: str = os.getenv("RP_URL")
    AS_URL: str = os.getenv("AS_URL")
    RS_URL: str = os.getenv("RS_URL")
    SCA_URL: str = os.getenv("SCA_URL")

    OAUTH_CODE_CHALLENGE_METHOD: str = os.getenv("OAUTH_CODE_CHALLENGE_METHOD")
    OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS: list[str] = os.getenv("OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS")

    # OID4VP Default Flow = Same Device Flow
    OAUTH_CLIENT_ID: str = os.getenv("OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET: str = os.getenv("OAUTH_CLIENT_SECRET")
    OAUTH_REDIRECT_URL: str = os.getenv("OAUTH_REDIRECT_URL")

    # OID4VP Cross Device Flow
    OAUTH_CROSS_DEVICE_FLOW_CLIENT_ID: str = os.getenv("OAUTH_CROSS_DEVICE_FLOW_CLIENT_ID")
    OAUTH_CROSS_DEVICE_FLOW_CLIENT_SECRET: str = os.getenv("OAUTH_CROSS_DEVICE_FLOW_CLIENT_SECRET")
    OAUTH_CROSS_DEVICE_FLOW_REDIRECT_URL: str = os.getenv("OAUTH_CROSS_DEVICE_FLOW_REDIRECT_URL")

    # OID4VP Cross Device Flow
    OAUTH_TEST_FORM_CLIENT_ID: str = os.getenv("OAUTH_TEST_FORM_CLIENT_ID")
    OAUTH_TEST_FORM_CLIENT_SECRET: str = os.getenv("OAUTH_TEST_FORM_CLIENT_SECRET")
    OAUTH_TEST_FORM_REDIRECT_URL: str = os.getenv("OAUTH_TEST_FORM_REDIRECT_URL")

    OAUTH_USERNAME: str = os.getenv("OAUTH_USERNAME")
    OAUTH_PASSWORD: str = os.getenv("OAUTH_PASSWORD")

    SUPPORTED_DIGEST_ALGOS: dict = {
        "2.16.840.1.101.3.4.2.1": "SHA256"
    }

settings = Settings()
