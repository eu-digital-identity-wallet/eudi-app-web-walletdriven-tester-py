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

from flask import render_template

def handle_exception(e):
    return (
        render_template(
            "500.html",
            error="Sorry, an internal server error has occurred. Please try again later.",
            error_code="Internal Server Error",
        ),
        500,
    )

def page_not_found(e):
    return (
        render_template(
            "500.html",
            error_code="Page not found",
            error="Page not found. We're sorry, we couldn't find the page you requested.",
        ),
        404,
    )