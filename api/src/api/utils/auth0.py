from fastapi import Request, HTTPException, Depends
import httpx
import os
from jose import jwt

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
ALGORITHMS = ["RS256"]

async def get_token_auth_header(request: Request) -> str:
    """Parse barear token from header

    Args:
        request (Request): _description_

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        str: _description_
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization header must start with 'Bearer'")
    return parts[1]

async def get_current_user(token: str = Depends(get_token_auth_header)) -> dict:
    """Get current user from token

    Args:
        token (str, optional): _description_. Defaults to Depends(get_token_auth_header).

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        dict: _description_
    """
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            jwks = (await client.get(jwks_url)).json()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
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
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS, audience=API_AUDIENCE)
            return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    raise HTTPException(status_code=401, detail="Unable to parse token")
