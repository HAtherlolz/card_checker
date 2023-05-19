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


async def widget_url_by_guid(guid: str) -> str:
    url = f"{settings.MX_API}/users/{guid}/widget_urls"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.mx.api.v1+json"
    }

    data = {
        "widget_url": {
            "widget_type": "connect_widget",
            "color_scheme": "dark"
        }
    }

    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(login=settings.CLIENT_ID, password=settings.API_KEY)
        async with session.post(url=url, json=data, headers=headers, auth=auth) as response:
            res = await response.json()
    return res["widget_url"]["url"]


async def get_accounts(user_guid: str, member_guid: str) -> list:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.mx.api.v1+json"
    }
    accounts_dict = dict()
    accounts_dicts_list = list()
    url = f"{settings.MX_API}/users/{user_guid}/members/{member_guid}/accounts?page=1&records_per_page=100"
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(login=settings.CLIENT_ID, password=settings.API_KEY)
        async with session.get(url=url, headers=headers, auth=auth) as response:
            res = await response.json()
        if res["pagination"]["total_pages"] > 1:
            pages = res["pagination"]["total_pages"]
            for page in range(1, pages):
                url = f"{settings.MX_API}/users/{user_guid}/members/{member_guid}/accounts?page={page}&records_per_page=10"
                async with session.get(url=url, headers=headers, auth=auth) as response:
                    res = await response.json()
                    for account in res["accounts"]:
                        accounts_dict["guid"] = account["guid"]
                        accounts_dict["name"] = account["name"]
                        accounts_dicts_list.append(accounts_dict)
        else:
            for account in res["accounts"]:
                accounts_dict["guid"] = account["guid"]
                accounts_dict["name"] = account["name"]
                accounts_dicts_list.append(accounts_dict)
    return accounts_dicts_list




