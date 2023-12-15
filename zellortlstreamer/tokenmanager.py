import os.path
import time

import jwt

tokenExpirationSeconds = 120


class PrivateKeyFileNotFoundError(Exception):
    """Raised when the private key file was not found"""

    pass


class TokenManager:
    """Class fore generating jwt tokens"""

    def __init__(self, privkeyfilename, issuer, exp=tokenExpirationSeconds):
        if not os.path.isfile(privkeyfilename):
            raise PrivateKeyFileNotFoundError(privkeyfilename)

        self.issuer = issuer
        self.exp = exp

        file = open(privkeyfilename, 'r')
        self.privkey = file.read()
        file.close()

        self.key = "\n".join([l.lstrip() for l in self.privkey.split("\n")])
        self.header = {"alg": "RS256", "typ": "JWT"}

    def getToken(self):
        payload = {"iss": self.issuer, "exp": round(time.time())+self.exp}
        return jwt.encode(
            payload,
            self.key,
            algorithm='RS256',
            headers=self.header)
