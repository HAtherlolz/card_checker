import io

import openpyxl
from openpyxl.styles import Font

from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

import tempfile


async def get_excel_file(transactions: dict) -> UploadFile:
    """
        Getting data and creating excel file by them
    """

    # Makes excel by data
    workbook = openpyxl.Workbook()
    sheet_p = 1
    for account in transactions:
        if sheet_p == 1:
            sheet = workbook.active
            sheet.title = account
            sheet_p = 0
        else:
            sheet = workbook.create_sheet(title=account)
        bold_font = Font(bold=True)
        sheet['A1'].font = bold_font
        sheet['B1'].font = bold_font
        sheet['A1'] = "Category"
        sheet['B1'] = "Total Spent"
        iteration = 2
        for category in transactions[account]:
            for cat in category:
                a = f"A{iteration}"
                b = f"B{iteration}"
                sheet[a] = cat
                sheet[b] = category[cat]
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
