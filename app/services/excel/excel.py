import io

import openpyxl

from starlette.datastructures import UploadFile as StarletteUploadFile

import tempfile


async def get_excel_file(transactions: dict) -> None:
    """
        Getting data and creating excel file by them
    """
    workbook = openpyxl.Workbook()
    sheet_p = 1
    for account in transactions:
        if sheet_p == 1:
            sheet = workbook.active
            sheet.title = account
            sheet_p = 0
        else:
            sheet = workbook.create_sheet(title=account)
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


    # Create the first sheet and populate it with data
    # sheet1 = workbook.active
    # sheet1.title = "Sheet 1"
    # sheet1['A1'] = "Data 1"
    # sheet1['B1'] = "Data 2"
    #
    # # Create the second sheet and populate it with data
    # sheet2 = workbook.create_sheet(title="Sheet 2")
    # sheet2['A1'] = "Data 3"
    # sheet2['B1'] = "Data 4"

    bytes_stream = io.BytesIO()
    workbook.save(bytes_stream)

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    filename = "Analiz_of_card"

    with open(temp_file.name, "wb") as file:
        file.write(bytes_stream.getvalue())

    f = StarletteUploadFile(file=temp_file, filename=f"{filename}.xls")

    print("==========================", type(temp_file))
    print("1231231", f)
    return f
