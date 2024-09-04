from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from dotenv import load_dotenv
import os

load_dotenv()

MIDDLEWARE_API_KEY = os.getenv("MIDDLEWARE_API_KEY", "")


# Inialize bearer scheme
bearer_scheme = HTTPBearer()


class SystemSecurity:
    async def verify_api_key(
        self, cred: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ):
        if cred.credentials != MIDDLEWARE_API_KEY:
            return HTTPException(
                status_code=401, detail="You Are Unathorized To Access This"
            )
        return True
