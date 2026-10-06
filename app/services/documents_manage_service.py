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

import mimetypes

from werkzeug.utils import secure_filename
import base64, os
from app.core.config import settings

def get_mime_type_and_filename(document) -> tuple[str, str]:
    """Returns mime type and new filename for a signed document."""
    container = document["container"]
    ext = None
    if container == "ASiC-S":
        mime_type = "application/vnd.etsi.asic-s+zip"
        ext = ".zip"
    elif container == "ASiC-E":
        mime_type = "application/vnd.etsi.asic-e+zip"
        ext = ".zip"
    else:
        mime_type, _ = mimetypes.guess_type(document["filepath"])
    new_name = add_suffix_to_filename(os.path.basename(document["filepath"]), new_ext=ext)
    return mime_type, new_name


def get_base64_document(filename):
    base64_document = None
    with open(filename, 'rb') as document:
        base64_document = base64.b64encode(document.read()).decode("utf-8")

    return base64_document


def get_unique_filename(folder, filename):
    base, ext = os.path.splitext(filename)  # Split the filename into name and extension
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename


def save_document(document):
    filename = secure_filename(document.filename)
    filename = get_unique_filename(settings.DOCUMENTS_UPLOAD_FOLDER, filename)
    file_path = os.path.join(settings.DOCUMENTS_UPLOAD_FOLDER, filename)
    document.save(file_path)
    document.stream.seek(0)
    return file_path, filename


def save_document_with_name(document, filename):
    filename = secure_filename(filename)
    filename = get_unique_filename(settings.DOCUMENTS_UPLOAD_FOLDER, filename)
    file_path = os.path.join(settings.DOCUMENTS_UPLOAD_FOLDER, filename)

    with open(file_path, 'wb') as file:
        file.write(document)

    return file_path, filename


def add_suffix_to_filename(filename, suffix="_signed", new_ext=None):
    name, ext = os.path.splitext(filename)
    if new_ext is not None:
        return f"{name}{suffix}{new_ext}"
    return f"{name}{suffix}{ext}"


def get_documents_content_from_filepath(documents):
    documents_content = []
    for single_document in documents:
        path = single_document["filepath"]
        base64_pdf = get_base64_document(path)
        documents_content.append(base64_pdf)
    return documents_content