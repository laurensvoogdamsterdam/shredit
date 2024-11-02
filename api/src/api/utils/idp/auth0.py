import os

import httpx
import requests
from fastapi import HTTPException, Request
from jose import jwt
from jose.exceptions import JWTError

from api.exceptions import AuthError
from api.utils.idp.base import IdentityProvider

API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]
AUTH0_DOMAIN = os.getenv("AUTH0_ISSUER_BASE_URL")
SHARED_SECRET = os.getenv(
    "AUTH0_CLIENT_SECRET"
)  # Ensure you have this in your environment variables
AUTH0_ISSUER_BASE_URL = os.getenv("AUTH0_ISSUER_BASE_URL")


class Auth0IdentifyProvider(IdentityProvider):

    #  validate_token
    async def validate_token(self, token: str) -> dict:
        """Validate the token with the identity

        Args:
            token (str): _description_

        Returns:
            dict: _description_
        """
        try:
            jwks_url = f"{AUTH0_DOMAIN}/.well-known/jwks.json"
            async with httpx.AsyncClient() as client:
                jwks = (await client.get(jwks_url)).json()

            try:
                unverified_header = jwt.get_unverified_header(token)
            except jwt.JWTError as jwt_error:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Invalid header. "
                        "Use an RS256 signed JWT Access Token",
                    },
                    401,
                ) from jwt_error

            rsa_key = None
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:

                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
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
                    raise AuthError(
                        {"code": "token_expired", "description": "token is expired"},
                        401,
                    ) from expired_sign_error
                except jwt.JWTClaimsError as jwt_claims_error:
                    log.error(jwt_claims_error)
                    raise AuthError(
                        {
                            "code": "invalid_claims",
                            "description": "incorrect claims,"
                            " please check the audience and issuer",
                        },
                        401,
                    ) from jwt_claims_error
                except Exception as exc:
                    raise AuthError(
                        {
                            "code": "invalid_header",
                            "description": "Unable to parse authentication" " token.",
                        },
                        401,
                    ) from exc

                return payload

            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to find appropriate key",
                },
                401,
            )

        except Exception as e:
            log.error(e)
            raise HTTPException(status_code=401, detail="Invalid token")

        raise HTTPException(status_code=401, detail="Unable to parse token")

    async def get_user_info(self, token: str) -> dict:
        """Get user info from the token.

        Args:
            token (str): _description_

        Raises:
            Exception: _description_

        Returns:
            dict: _description_
        """
        url = "https://dev-cfhyeddof3167alv.eu.auth0.com/userinfo"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            json_data = response.json()
            json_data["auth_id"] = json_data["sub"]
            return json_data
        else:
            raise Exception(
                f"Error fetching user info: {response.status_code}, {response.text}"
            )
