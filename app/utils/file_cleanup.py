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

from datetime import datetime, timedelta
import os
import logging

log = logging.getLogger(__name__)

def delete_old_files(folder: str, max_age_minutes: int = 30):
    now = datetime.now()
    deleted = 0
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            continue
        file_age = now - datetime.fromtimestamp(os.path.getmtime(filepath))
        if file_age > timedelta(minutes=max_age_minutes):
            os.remove(filepath)
            log.info("Deleted old file: %s", filepath)
            deleted += 1
    log.info("Cleanup complete: deleted %d files from %s", deleted, folder)