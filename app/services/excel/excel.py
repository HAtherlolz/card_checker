import io

import openpyxl
from openpyxl.styles import Font, Alignment

from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

import tempfile


async def get_excel_file(transactions: dict, accounts_list: list) -> UploadFile:
    """
        Getting data and creating excel file by them
    """

    # Makes excel by data
    workbook = openpyxl.Workbook()
    # Sheet 1
    bold_font = Font(bold=True)
    sheet = workbook.active
    sheet.title = "Total spent"
    sheet.column_dimensions['A'].width = 20
    sheet.column_dimensions['B'].width = 15
    sheet['A1'].alignment = Alignment(horizontal='center', vertical='center')
    sheet['B1'].alignment = Alignment(horizontal='center', vertical='center')
    sheet['A1'].font = bold_font
    sheet['B1'].font = bold_font
    sheet['A1'] = "Category"
    sheet['B1'] = "Total Spent"

    iteration = 2
    for cat in transactions:
        a = f"A{iteration}"
        b = f"B{iteration}"
        sheet[a] = cat
        sheet[b] = transactions[cat]
        iteration += 1

    # Sheet 2
    sheet_accounts = workbook.create_sheet(title="Products")
    sheet_accounts.column_dimensions['A'].width = 25
    sheet_accounts['A1'].alignment = Alignment(horizontal='center', vertical='center')
    sheet_accounts['A1'].font = bold_font
    sheet_accounts['A1'] = "Products"

    iteration = 2
    for account in accounts_list:
        a = f"A{iteration}"
        sheet_accounts[a] = account["name"]
        iteration += 1

    bytes_stream = io.BytesIO()
    workbook.save(bytes_stream)

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    filename = "Analiz_of_card"

    with open(temp_file.name, "wb") as file:
        file.write(bytes_stream.getvalue())

    f = StarletteUploadFile(file=temp_file, filename=f"{filename}.xls")

    return f
