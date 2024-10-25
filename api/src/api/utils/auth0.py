import os

import httpx
import requests
from fastapi import HTTPException, Request
from jose import jwt
from jose.exceptions import JWTError

from api.exceptions import AuthError

API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]
AUTH0_DOMAIN=os.getenv('AUTH0_ISSUER_BASE_URL')
SHARED_SECRET = os.getenv("AUTH0_CLIENT_SECRET")  # Ensure you have this in your environment variables
AUTH0_ISSUER_BASE_URL = os.getenv("AUTH0_ISSUER_BASE_URL")  


from api.utils.logger import log


async def get_token_auth_header() -> str:
    """Obtains the access token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    if len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    if len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)

    token = parts[1]
    return token

async def get_token_auth_header(request: Request) -> str:
    """Parse bearer token from header."""
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization header must start with 'Bearer'")
    return parts[1]

async def get_current_user(token: str) -> dict:
    """Get current user from token."""
    try:
        jwks_url = f"{AUTH0_DOMAIN}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            jwks = (await client.get(jwks_url)).json()

        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError as jwt_error:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401) from jwt_error
        
        rsa_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer=AUTH0_ISSUER_BASE_URL + "/",
                )
            except jwt.ExpiredSignatureError as expired_sign_error:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401) from expired_sign_error
            except jwt.JWTClaimsError as jwt_claims_error:
                log.error(jwt_claims_error)
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401) from jwt_claims_error
            except Exception as exc:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401) from exc

            return payload
            
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)


    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=401, detail="Invalid token")

    raise HTTPException(status_code=401, detail="Unable to parse token")



def get_user_info(access_token):
    url = "https://dev-cfhyeddof3167alv.eu.auth0.com/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching user info: {response.status_code}, {response.text}")
