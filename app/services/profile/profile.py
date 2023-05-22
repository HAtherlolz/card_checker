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
        async with session.post(url=url, json=data, headers=settings.MX_HEADERS, auth=auth) as response:
            res = await response.json()
    return res["user"]["guid"]


async def widget_url_by_guid(guid: str) -> str:
    """
        Create unique widget url for frontend,
        this url can be used one time
    """

    url = f"{settings.MX_API}/users/{guid}/widget_urls"

    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(login=settings.CLIENT_ID, password=settings.API_KEY)
        async with session.post(
                url=url, json=settings.MX_WIDGET_SETTINGS, headers=settings.MX_HEADERS, auth=auth) as response:
            res = await response.json()
    return res["widget_url"]["url"]


async def get_accounts(user_guid: str, member_guid: str) -> list:
    """ Get all accounts by user_guid and member_guid """
    accounts_dicts_list = list()
    url = f"{settings.MX_API}/users/{user_guid}/members/{member_guid}/accounts?page=1&records_per_page=100"
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(login=settings.CLIENT_ID, password=settings.API_KEY)
        async with session.get(url=url, headers=settings.MX_HEADERS, auth=auth) as response:
            res = await response.json()
        if res["pagination"]["total_pages"] > 1:
            pages = res["pagination"]["total_pages"]
            for page in range(1, pages + 1):
                url = f"{settings.MX_API}/users/{user_guid}/members/{member_guid}/" \
                      f"accounts?page={page}&records_per_page=100"
                async with session.get(url=url, headers=settings.MX_HEADERS, auth=auth) as response:
                    res = await response.json()
                    accounts_dicts_list = await write_accounts(res["accounts"], accounts_dicts_list)
        else:
            accounts_dicts_list = await write_accounts(res["accounts"], accounts_dicts_list)
    return accounts_dicts_list


async def write_accounts(accounts: dict, accounts_dicts_list: list) -> list:
    """
        Gets accounts object, gets guid, name, writes to new dict and write to list
    """
    for account in accounts:
        accounts_dict = dict()
        accounts_dict["guid"] = account["guid"]
        accounts_dict["name"] = account["name"]
        accounts_dicts_list.append(accounts_dict)
    return accounts_dicts_list


async def get_transactions(user_guid: str, accounts_list: list) -> dict:
    """
        Gets all transactions by each account, gets from transactions objects category and amount of spent,
        counts the total spent by each category
    """
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
            async with session.get(url=url, headers=settings.MX_HEADERS, auth=auth) as response:
                res = await response.json()

            # If pages > 1, does requests from first to last page
            if res["pagination"]["total_pages"] > 1:
                pages = res["pagination"]["total_pages"]

                for page in range(1, pages + 1):
                    url = f"{settings.MX_API}/users/{user_guid}/accounts/{account_guid}/" \
                          f"transactions?from_date={from_date}&to_date={to_date}&page={page}&records_per_page=100"
                    async with session.get(url=url, headers=settings.MX_HEADERS, auth=auth) as response:
                        res = await response.json()
                        for transaction in res["transactions"]:
                            transactions_dict[transaction["category"]] += transaction["amount"]
                transactions_dicts_list.append(dict(transactions_dict))
            else:
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
