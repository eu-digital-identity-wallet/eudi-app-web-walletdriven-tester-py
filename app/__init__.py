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

"""
Application Initialization File:
Handles application setup, configuration, and exception handling.
"""

import os, sys

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_session import Session
from flask_cors import CORS
from app.api.endpoints.auth import routes as auth_routes
from app.api.endpoints.main import routes as main_routes
from app.api.endpoints.document import routes as document_routes
from app.api.endpoints.credentials import routes as credentials_routes
from app.api.endpoints.relying_party import routes as relying_party_routes
from app.api.endpoints.dependencies import page_not_found, handle_exception
from app.core.config import settings
from app.core.logging import configure_logging
from app.utils.file_cleanup import delete_old_files

# Extend system path to include the current directory
sys.path.append(os.path.dirname(__file__))

def create_app() -> Flask:
    configure_logging()

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path='/tester/static'
    )

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: delete_old_files(settings.UPLOAD_FOLDER, max_age_minutes=60),
        trigger="interval",
        minutes=720  # run every 12 hours
    )
    scheduler.start()

    app.config.from_object(settings)

    Session(app)
    CORS(app, supports_credentials=True)

    app.register_blueprint(auth_routes.auth_routes)
    app.register_blueprint(main_routes.base_routes)
    app.register_blueprint(document_routes.documents_routes)
    app.register_blueprint(credentials_routes.credentials_routes)
    app.register_blueprint(relying_party_routes.relying_party_routes)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(Exception, handle_exception)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()