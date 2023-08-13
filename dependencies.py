token_auth_scheme = HTTPBearer()


async def get_token(
    clientid: str, authorization: str = Header(default="Bearer ")
) -> str:
    _, token = authorization.split(" ")
    key_vault_service = AWSSecretsManagerService()
    try:
        api_key = key_vault_service.get_secret("api-key")
    except:
        # pylint: disable=W0707
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to fetch API Key"
        )

    # Simulate a database query to find a known token
    if token != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key"
        )
    return token


async def get_client_raw():
    # create a new client for each request
    async with httpx.AsyncClient() as client:
        # yield the client to the endpoint function
        yield client
        # close the client when the request is done
