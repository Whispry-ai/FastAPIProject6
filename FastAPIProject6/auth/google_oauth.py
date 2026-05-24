# auth/google_oauth.py

from authlib.integrations.starlette_client import OAuth
import os

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)
import os
print("CLIENT ID:", os.getenv("GOOGLE_CLIENT_ID"))
print("CLIENT SECRET:", os.getenv("GOOGLE_CLIENT_SECRET"))
