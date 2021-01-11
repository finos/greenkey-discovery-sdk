#!/usr/bin/env python3

import os

CONFIG = {
    "GKT_USERNAME": os.environ.get("GKT_USERNAME", ""),
    "GKT_SECRETKEY": os.environ.get("GKT_SECRETKEY", ""),
    "GKT_API": os.environ.get("GKT_API", "https://scribeapi.greenkeytech.com/"),
}
if not CONFIG["GKT_USERNAME"] or not CONFIG["GKT_SECRETKEY"]:
    CONFIG["LICENSE_KEY"] = os.environ.get("LICENSE_KEY", "")
