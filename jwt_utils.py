import jwt
import datetime

SECRET_KEY = "your-secret-key"  # 本番では安全な値に変更してください


def create_jwt_token(data: dict, expires_delta: int = 60 * 60 * 24 * 7):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=expires_delta
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_jwt_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"payload": decoded, "valid": True}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "invalid"}
