import asyncio
import json
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message

from src.config import BOT_TOKEN, INPUT_DATE_FORMAT, OUTPUT_DATE_FORMAT

dp = Dispatcher()


def parse_date(date: str) -> datetime:
    return datetime.strptime(date, INPUT_DATE_FORMAT)


def format_date(date: datetime) -> str:
    return date.strftime(OUTPUT_DATE_FORMAT)


def prepare_data(report_data) -> None:
    total_hours = 0

    report_data['report_period'] = {
        'start_date': parse_date(report_data['report_period']['start_date']),
        'end_date': parse_date(report_data['report_period']['end_date'])
    }

    for i, day in enumerate(report_data['days']):
        day_total_hours = 0
        for project in day['projects']:
            total_hours += project['hours']
            day_total_hours += project['hours']

        day['date'] = parse_date(day['date'])
        day['total_hours'] = day_total_hours

    report_data['total_hours'] = total_hours


def generate_report(data) -> str:
    text = ""

    text += "```Отчёт\n"

    formatted_start_date = format_date(data['report_period']['start_date'])
    formatted_end_date = format_date(data['report_period']['end_date'])

    text += f"С {formatted_start_date} по {formatted_end_date}\n\n"

    text += f"ИТОГО: {data['total_hours']} ч.\n"

    for i, day in enumerate(data['days']):
        if day['total_hours'] == 0:
            continue

        text += "\n"

        text += f"{format_date(day['date'])}\n"
        text += f"Итого: {day['total_hours']} ч.\n"

        for project in day['projects']:
            text += f"{project['name']} - {project['hours']} ч.\n"
            for task in project['tasks']:
                text += f" - {task}\n"

    text += "```"

    return text


@dp.message()
async def handle_message(message: Message) -> None:
    data = json.loads(message.text)
    prepare_data(data)

    report = generate_report(data)

    await message.reply(report)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='MarkdownV2'))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
