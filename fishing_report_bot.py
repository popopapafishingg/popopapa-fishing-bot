import os
import requests

print("ENV keys:", [k for k in os.environ.keys() if "LINE" in k or "TOKEN" in k or "USER" in k or "POPO" in k])

def clean_env(name):
    v = os.getenv(name, "")
    v = v.strip().strip('"').strip("'")
    v = v.replace("\n", "").replace("\r", "").replace(" ", "")
    if "=" in v:
        v = v.split("=", 1)[1]
    return v

LINE_TOKEN = clean_env("POPO_LINE_TOKEN")
USER_ID = clean_env("USER_ID")

print("POPO_LINE_TOKEN長:", len(LINE_TOKEN))
print("USER_ID長:", len(USER_ID))
