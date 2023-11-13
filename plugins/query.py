import os, time, asyncio,sys
import humanize
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.utils import Compress_Stats, Skip, CompressVideo
from helper.database import db
from script import Txt

@Client.on_callback_query()
async def Cb_Handle(bot:Client, query:CallbackQuery):
    data = query.data

    if data == 'help':

        btn = [
            [InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='home')]
        ]

        await query.message.edit(text=Txt.HELP_MSG, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        

    if data == 'home':
        btn = [
            [InlineKeyboardButton(text='❗ Hᴇʟᴘ', callback_data='help'), InlineKeyboardButton(text='🌨️ Aʙᴏᴜᴛ', callback_data='about')],
            [InlineKeyboardButton(text='📢 Uᴘᴅᴀᴛᴇs', url='https://t.me/AIORFT'), InlineKeyboardButton(text='💻 Dᴇᴠᴇʟᴏᴘᴇʀ', callback_data='https://t.me/Snowball_Official')]
        ]
        await query.message.edit(text=Txt.PRIVATE_START_MSG.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(btn))


    if data == 'stats':
        try:
            downpath = f"Downloads/{query.from_user.id}/{os.listdir(f'Downloads/{query.from_user.id}')[0]}"
            encodepath = f"Encode/{query.from_user.id}/{os.listdir(f'Encode/{query.from_user.id}')[0]}"


            await Compress_Stats(e=query, inp=downpath, outp=encodepath, userid=query.from_user.id)
            
        except Exception as e:
            print(e)
    
    elif data == 'Skip':
        try:
            await Skip(query, query.from_user.id)
        except Exception as e:
            print(e)
        
    elif data == 'compress':
        BTNS = [
        [InlineKeyboardButton(text='Basic Compression', callback_data='basiccomp')],
        [InlineKeyboardButton(text='Higly Compression', callback_data='highlycomp')],
        [InlineKeyboardButton(text='Custom Compression', callback_data='customcomp')],
        [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='option')]
    ]
        await query.message.edit(text='**Select the Compression Method Below 👇 **', reply_markup=InlineKeyboardMarkup(BTNS))
        
    
    elif data == 'option':
        file = getattr(query.message.reply_to_message, query.message.reply_to_message.media.value)
        
        text = f"""**__What do you want me to do with this file.?__**\n\n**File Name** :- `{file.file_name}`\n\n**File Size** :- `{humanize.naturalsize(file.file_size)}`"""
        buttons = [[InlineKeyboardButton("📝 RENAME 📝", callback_data="rename")],
                    [InlineKeyboardButton("🗜️ COMPRESS 🗜️", callback_data="compress")]]
        
        await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        
    elif data == 'basiccomp':
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            await CompressVideo(bot=bot, query=query, ffmpegcode='-vcodec libx265 -crf 24', c_thumb=c_thumb)
            
        except Exception as e:
            print(e)
    
    elif data == 'highlycomp':
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            await CompressVideo(bot=bot, query=query, ffmpegcode='-vcodec libx265 -crf 30', c_thumb=c_thumb)
            
        except Exception as e:
            print(e)
    
    elif data == 'customcomp':

        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            ffmpeg_code = await db.get_ffmpegcode(query.from_user.id)

            if ffmpeg_code:
                await CompressVideo(bot=bot, query=query, ffmpegcode=ffmpeg_code, c_thumb=c_thumb)
            
            else:
                BUTT = [
                    [InlineKeyboardButton(text='Sᴇᴛ Fғᴍᴘᴇɢ Cᴏᴅᴇ', callback_data='setffmpeg')],
                    [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='compress')]
                ]
                await query.message.edit(text="You Don't Have Any Custom FFMPEG Code. 🛃", reply_markup=InlineKeyboardMarkup(BUTT))
        except Exception as e:
            print(e)
        
    elif data == 'setffmpeg':
        ffmpeg_code = await bot.ask(text=Txt.SEND_FFMPEG_CODE , chat_id= query.from_user.id, filters = filters.text, timeout=60, disable_web_page_preview=True)
        SnowDev = await query.message.reply_text(text="**Setting Your FFMPEG CODE**\n\nPlease Wait...")
        await db.set_ffmpegcode(query.from_user.id, ffmpeg_code.text)
        await SnowDev.edit("✅️ __**Fғᴍᴘᴇɢ Cᴏᴅᴇ Sᴇᴛ Sᴜᴄᴄᴇssғᴜʟʟʏ**__")

    elif data == 'about':
        BUTN = [
            [[InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='home')]]
        ]
        botuser = await bot.get_me()
        query.message.edit(Txt.ABOUT_TXT.format(botuser.username), reply_markup=InlineKeyboardMarkup(BUTN))


    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()
