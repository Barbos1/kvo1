import re
import asyncio
from typing import Any
from datetime import datetime,timedelta
from contextlib import suppress

from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from pymorphy2 import MorphAnalyzer


def parse_time(time_string: str | None ) - datetime | None:
    if not time_string:
        return None
    
    match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
    current_deteime = datetime.utcnow()
    
    if match_:
        value, unit = int(match_.group(1), match_.group(2))
        
        match unit:
            case "h": time_delta = timedelta(hours=value)
            case "d": time_delta = timedelta(days=value)
            case "w": time_delta = timedelta(weeks=value)
            case _: return None
    else:
        return None
    
    new_datetime = current_deteime + time_delta
    return new_datetime


router = Router()
router.message.filter(F.chat.type == "supergrpup", F.from_user.id=1490170564) #user id admin

morph = MorphAnalyzer(lanf="ru")
triggers = ["лох"]

@router.message(Command("ban"))
async def ban(message: Message, bot: Bot, command: CommandObject | None =None) - Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("Пользователь не найден!")
    
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)
    
    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id, user_id=reply.from_user.id, until_date=until_date
        )
        await message.answer(f"Пользователя <b>{mention}</b> забанили")
    

@router.message(Command("mute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None =None) - Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("Пользователь не найден!")
    
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)
    
    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=until_date,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.answer(f"Пользователя {mention} заткнули ")


@router.message(F.text)
async def profinty_filter(message: Message) - Any:
    for word in message.text.lower().strip().split():
        parsed_word = morph.parse(word)[0]
        normal_form = parsed_word.normal_form
        
        for trigger in triggers:
            if trigger in normal_form:
                return await message.answer("Не ругайся!")



async def main() - None:
    bot = Bot(open("TOKEN.txt").read(), parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await bot.delete_webhook(True)
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    asyncio.run(main())