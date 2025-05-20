import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsToolkit:
    """
    Обёртка для работы с Google Sheets:
      - Чтение следующей идеи со статусом 'ожидание'
      - Отметка идеи как выполненной ('выполнено') и запись времени публикации
    """

    def __init__(
        self,
        credentials_json: str,
        sheet_id: str,
        worksheet_name: str = 'work'
    ):
        """
        :param credentials_json: путь к JSON-файлу Service Account
        :param sheet_id: ID Google Sheet
        :param worksheet_name: имя листа
        """
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id)
        self.worksheet = self.sheet.worksheet(worksheet_name)
        logger.info(
            "Initialized Google Sheets: %s (worksheet: %s)",
            sheet_id,
            worksheet_name,
        )

    def get_next_idea(self) -> Optional[Dict[str, Any]]:
        """
        Находит первую строку со статусом 'ожидание'.

        :return: словарь {'row', 'idea', 'examples'} или None
        """
        try:
            records = self.worksheet.get_all_records()
            for idx, record in enumerate(records, start=2):
                status = record.get('status', '').strip().lower()
                if status == 'ожидание':
                    idea = record.get('idea', '') or record.get('title', '')
                    examples = record.get('examples', '')
                    logger.info("Found pending idea at row %s: %s", idx, idea)
                    return {'row': idx, 'idea': idea, 'examples': examples}
            logger.info("No pending ideas found in sheet")
            return None
        except Exception as e:
            logger.error("Error in get_next_idea: %s", e)
            raise

    def mark_done(self, row: int) -> None:
        """
        Помечает запись в строке row как 'выполнено' и записывает текущее время в колонку 'scheduled'.
        """
        try:
            status_col = self._status_col()
            scheduled_col = self._scheduled_col()

            self.worksheet.update_cell(row, status_col, 'выполнено')
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.worksheet.update_cell(row, scheduled_col, now_str)
            logger.info("Row %s marked as done at %s", row, now_str)
        except Exception as e:
            logger.error("Error in mark_done for row %s: %s", row, e)
            raise

    def _status_col(self) -> int:
        """
        Определяет номер колонки 'status' в шапке листа.
        """
        header = self.worksheet.row_values(1)
        try:
            return header.index('status') + 1
        except ValueError:
            msg = "Column 'status' not found in header"
            logger.error(msg)
            raise Exception(msg)

    def _scheduled_col(self) -> int:
        """
        Определяет номер колонки 'scheduled' в шапке листа.
        """
        header = self.worksheet.row_values(1)
        try:
            return header.index('scheduled') + 1
        except ValueError:
            msg = "Column 'scheduled' not found in header"
            logger.error(msg)
            raise Exception(msg)