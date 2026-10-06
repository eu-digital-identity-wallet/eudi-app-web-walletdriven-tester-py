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
from logging.config import dictConfig
from app.core.config import settings

def configure_logging():
    os.makedirs("logs", exist_ok=True)

    is_dev = settings.ENV == "dev"

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(module)s.%(funcName)s:%(lineno)d %(name)s: - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/walletdriven_rp_logs.log",
                "when": "D",
                "interval": 7, # a new file for every week
                "backupCount": 5, # the number of files that will be retained on the disk
                "formatter": "default",
            },
        },
        "loggers": {
            "werkzeug": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            }
        },
        "root": {
            "level": "DEBUG" if is_dev else "INFO",
            "handlers": ["console"] if is_dev else ["file"],
        },
    })