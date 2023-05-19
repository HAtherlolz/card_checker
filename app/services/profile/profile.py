import aiohttp

from config.conf import settings

from pydantic import EmailStr


async def register_user(email: EmailStr) -> str:
    """
        Register user in mx api
    """
    url = f"{settings.MX_API}/users"
    email_name = email.split('@')

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.mx.api.v1+json"
    }

    data = {
      "user": {
        "id": f"{email_name[0]}_",
        "is_disabled": False,
        "email": email,
        "metadata": f"{email}"
      }
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(login=settings.CLIENT_ID, password=settings.API_KEY)
        async with session.post(url=url, json=data, headers=headers, auth=auth) as response:
            res = await response.json()
    return res["user"]["guid"]
