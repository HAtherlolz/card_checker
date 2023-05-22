import aiohttp

from datetime import datetime
from dateutil.relativedelta import relativedelta

from collections import defaultdict

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

    accounts_dicts_list = list()
    url = f"{settings.MX_API}/users/{user_guid}/members/{member_guid}/accounts?page=1&records_per_page=100"
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(login=settings.CLIENT_ID, password=settings.API_KEY)
        async with session.get(url=url, headers=headers, auth=auth) as response:
            res = await response.json()
        print("===================================total_pages=================", res["pagination"]["total_pages"])
        print("===================================current_page=================", res["pagination"]["current_page"])
        print("===================================per_page=================", res["pagination"]["per_page"])
        print("===================================total_entries=================", res["pagination"]["total_entries"])
        if res["pagination"]["total_pages"] > 1:
            print("SMTHS")
            pages = res["pagination"]["total_pages"]
            for page in range(1, pages + 1):
                url = f"{settings.MX_API}/users/{user_guid}/members/{member_guid}/" \
                      f"accounts?page={page}&records_per_page=100"
                async with session.get(url=url, headers=headers, auth=auth) as response:
                    res = await response.json()
                    accounts_dicts_list = await write_accounts(res["accounts"], accounts_dicts_list)
        else:
            print("SMTHS123")
            accounts_dicts_list = await write_accounts(res["accounts"], accounts_dicts_list)
    return accounts_dicts_list


async def write_accounts(accounts: dict, accounts_dicts_list: list) -> list:
    for account in accounts:
        accounts_dict = dict()
        accounts_dict["guid"] = account["guid"]
        accounts_dict["name"] = account["name"]
        accounts_dicts_list.append(accounts_dict)
    return accounts_dicts_list


async def get_transactions(user_guid: str, accounts_list: list) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.mx.api.v1+json"
    }

    transactions_by_account_dict = dict()

    # Gets dates range from now to 24 month back
    from_date, to_date = await get_dates()

    for account in accounts_list:
        transactions_dict = defaultdict(int)
        transactions_dicts_list = list()
        # Getting account guid from list
        account_guid = account["guid"]
        account_name = account["name"]
        # Getting check request to check amount of pages
        url = f"{settings.MX_API}/users/{user_guid}/accounts/{account_guid}/" \
              f"transactions?from_date={from_date}&to_date={to_date}&page=1&records_per_page=100"
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(login=settings.CLIENT_ID, password=settings.API_KEY)
            async with session.get(url=url, headers=headers, auth=auth) as response:
                res = await response.json()
            print("===================================total_pages=================", res["pagination"]["total_pages"])
            print("===================================current_page=================", res["pagination"]["current_page"])
            print("===================================per_page=================", res["pagination"]["per_page"])
            print("===================================total_entries=================", res["pagination"]["total_entries"])
            # If pages > 1, does requests from first to last page
            if res["pagination"]["total_pages"] > 1:
                print("TUTA")
                pages = res["pagination"]["total_pages"]

                for page in range(1, pages + 1):
                    url = f"{settings.MX_API}/users/{user_guid}/accounts/{account_guid}/" \
                          f"transactions?from_date={from_date}&to_date={to_date}&page={page}&records_per_page=100"
                    async with session.get(url=url, headers=headers, auth=auth) as response:
                        res = await response.json()
                        for transaction in res["transactions"]:
                            print("=--=-==--==-=-=-===-==-=-=-=-=-=-=-=-==-=-==-=", transaction["amount"])
                            transactions_dict[transaction["category"]] += transaction["amount"]
                            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", transactions_dict)
                transactions_dicts_list.append(dict(transactions_dict))
            else:
                print("TUTA2")
                for transaction in res["transactions"]:
                    transactions_dict[transaction["category"]] += transaction["amount"]
                transactions_dicts_list.append(dict(transactions_dict))
        transactions_by_account_dict[account_name] = transactions_dicts_list
    return transactions_by_account_dict


async def get_dates() -> tuple[str, str]:
    """ Gets dates range from now to 24 month back """
    date_to = datetime.now()
    from_to = datetime.now() - relativedelta(months=24)
    return str(from_to)[:10], str(date_to)[:10]
