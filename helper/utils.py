import asyncio
import math, time
import sys
import shutil
import signal
import os
from pathlib import Path
from datetime import datetime
import psutil
from pytz import timezone
from config import Config
from script import Txt
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:        
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["⬢" for i in range(math.floor(percentage / 5))]),
            ''.join(["⬡" for i in range(20 - math.floor(percentage / 5))])
        )            
        tmp = progress + Txt.PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),            
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",               
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close")]])                                               
            )
        except:
            pass

def humanbytes(size):    
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ, ") if seconds else "") + \
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    return tmp[:-2] 

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def send_log(b, u):
    if Config.LOG_CHANNEL is not None:
        botusername = await b.get_me()
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        await b.send_message(
            Config.LOG_CHANNEL,
            f"**--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--**\n\nUꜱᴇʀ: {u.mention}\nIᴅ: `{u.id}`\nUɴ: @{u.username}\n\nDᴀᴛᴇ: {date}\nTɪᴍᴇ: {time}\n\nBy: @{botusername.username}"
        )
        


async def CANT_CONFIG_GROUP_MSG(client, message):
    botusername = await client.get_me()
    btn = [
        [InlineKeyboardButton(text='Bᴏᴛ Pᴍ', url=f'https://t.me/{botusername.username}')]
    ]
    ms = await message.reply_text(text="Sᴏʀʀʏ Yᴏᴜ Cᴀɴ'ᴛ Cᴏɴғɪɢ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Iɴ Gʀᴏᴜᴘ\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴛ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴛʜᴇɴ ᴜsᴇ ᴄᴏᴍᴍᴀɴᴅs ɪɴ ᴘʀɪᴠᴀᴛᴇ", reply_to_message_id = message.id, reply_markup=InlineKeyboardMarkup(btn))

    await asyncio.sleep(10)
    await ms.delete()


async def Compress_Stats(e, inp, outp, userid):
    try:
        ot = humanbytes(int((Path(outp).stat().st_size)))
        ov = humanbytes(int(Path(inp).stat().st_size))
        processing_file_name = inp.replace(f"Downloads/{userid}/", "").replace(f"_", " ")
        ans = f"Processing Media: {processing_file_name}\n\nDownloaded: {ov}\n\nCompressed: {ot}"
        await e.answer(ans, cache_time=0, show_alert=True)
    except Exception as er:
        print(er)
        await e.answer(
            "Someting Went Wrong.\nSend Media Again.", cache_time=0, alert=True
        )

async def Skip(e, userid):
    try:
        await e.message.delete()
        os.system(f"rm -rf Downloads/{userid}*")
        os.system(f"rm -rf Encode/{userid}*")
        for proc in psutil.process_iter():
            processName = proc.name()
            processID = proc.pid
            print(processName , ' - ', processID)
            if(processName == "ffmpeg"):
             os.kill(processID,signal.SIGKILL)
    except Exception as e:
        pass
    try:
        shutil.rmtree(f'Downloads' + '/' + str(userid))
        shutil.rmtree(f'Encode' + '/' + str(userid))
    except Exception as e:
        pass
    
    return

async def CompressVideo(bot, query, ffmpegcode, c_thumb):
    try:
        media = query.message.reply_to_message
        file = getattr(media , media.media.value)
        Download_DIR = f"Downloads/{query.from_user.id}"
        Output_DIR = f"Encode/{query.from_user.id}"
        File_Path = f"Downloads/{query.from_user.id}/{file.file_name}"
        if file.mime_type.split('/')[0] == 'audio':
            Output_Path = f"Encode/{query.from_user.id}/{str(file.file_name).split('.')[0]}.mp4"
        else:
            Output_Path = f"Encode/{query.from_user.id}/{str(file.file_name).split('.')[0]}.mkv"
        
        ms = await query.message.edit('⚠️__**Please wait...**__\n**Tʀyɪɴɢ Tᴏ Dᴏᴡɴʟᴏᴀᴅɪɴɢ....**')

        try:
            if os.path.isdir(Download_DIR) and os.path.isdir(Output_DIR):
                return await ms.edit(
                    "**Already One Process is Going On! \nPlease Wait Until It's Get Finished 😕!**"
                )
            else:
                os.makedirs(Download_DIR)
                os.makedirs(Output_DIR)

                dl = await bot.download_media(
                    message=file,
                    file_name=File_Path,
                    progress=progress_for_pyrogram,
                    progress_args=("\n⚠️__**Please wait...**__\n\n☃️ **Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time())
                )
        except Exception as e:
            return await ms.edit(str(e))

        await ms.edit(
            "**🗜 Compressing...**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Sᴛᴀᴛs', callback_data='stats')],
                [InlineKeyboardButton(text='Cᴀɴᴄᴇʟ', callback_data='Skip')]
            ])
        )
        
        cmd = f"""ffmpeg -i {dl} {ffmpegcode} {Output_Path}"""

        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        

        stdout, stderr = await process.communicate()
        er = stderr.decode()

        try:
            if er:
                await ms.edit(str(er) + "\n\n**Error**")
                shutil.rmtree(f"Downloads/{query.from_user.id}")
                shutil.rmtree(f"Encode/{query.from_user.id}")
        except BaseException:
            pass
    

        # Now Uploading to the User
        # Clean up resources

        if (file.thumbs or c_thumb):
            if c_thumb:
                ph_path = await bot.download_media(c_thumb)
            else:
                ph_path = await bot.download_media(file.thumbs[0].file_id)

        await ms.edit("⚠️__**Please wait...**__\n**Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....**")
        await bot.send_document(
                query.from_user.id,
                document=Output_Path,
                thumb=ph_path,
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n🌨️ **Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
        
        if query.message.chat.type == enums.ChatType.SUPERGROUP:
            botusername = await bot.get_me()
            await ms.edit(f"Hey {query.from_user.mention},\n\nI Have Send Compressed File To Your Pm", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Bᴏᴛ Pᴍ", url=f'https://t.me/{botusername.username}')]]))
        else:
            await ms.delete()

        try:
            shutil.rmtree(f"Downloads/{query.from_user.id}")
            shutil.rmtree(f"Encode/{query.from_user.id}")
            os.remove(ph_path)
        except BaseException:
            pass
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
