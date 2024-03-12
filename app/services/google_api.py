import copy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"

TITLE = 'Отчет от {}'
ROW_COUNT = 100
COLUMN_COUNT = 11

SPREADSHEET_BODY = dict(
    properties=dict(
        title=TITLE,
        locale='ru_RU',
    ),
    sheets=[dict(
        properties=dict(
            sheetType='GRID',
            sheetId=0,
            title='Лист1',
            gridProperties=dict(
                rowCount=ROW_COUNT,
                columnCount=COLUMN_COUNT,
            )
        )
    )]
)

HEADER_BODY = [[TITLE.rsplit(maxsplit=1)],
               ['Топ проектов по скорости закрытия'],
               ['Название проекта', 'Время сбора', 'Описание']]


async def spreadsheets_create(
    wrapper_services: Aiogoogle,
    now_date_time: datetime = datetime.now().strftime(FORMAT)
) -> tuple[str, str]:
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = copy.deepcopy(SPREADSHEET_BODY)
    spreadsheet_body['properties']['title'].format(now_date_time)
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        )
    )


async def spreadsheets_update_value(
    spreadsheetid: str,
    charity_projects: list,
    wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    header_body = copy.deepcopy(HEADER_BODY)
    header_body[0][1].format(now_date_time)
    table_values = [
        *HEADER_BODY,
        *[[project.name,
           str(project.close_date - project.create_date),
           project.description]
          for project in charity_projects]
    ]
    if (len(table_values) > ROW_COUNT or max(
        table_values, key=len
    ) > COLUMN_COUNT):
        raise OverflowError('Размер данных слишком большой')
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=f'R1C1:R{ROW_COUNT}C{COLUMN_COUNT}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
