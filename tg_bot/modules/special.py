from io import BytesIO
from tg_bot.modules.helper_funcs.extraction import extract_user
from time import sleep
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from tg_bot.modules.helper_funcs.chat_status import is_user_ban_protected, bot_admin
from mal import AnimeSearch,Anime
import tg_bot.modules.sql.users_sql as sql
from tg_bot import dispatcher, OWNER_ID, LOGGER
from tg_bot.modules.helper_funcs.filters import CustomFilters
import asyncio
from rotten_tomatoes_client import RottenTomatoesClient
import requests,bs4,re
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode

USERS_GROUP = 4
rep="""  ⚡⚡{title}⚡⚡

Rating: {rate}⭐ 
Genres:{genre}👺
URL: {url}"""

@run_async
def echo1(bot: Bot, update: Update, args: List[int]):
    update.message.reply_text(update.message.text)

@run_async
def echo(bot: Bot, update: Update, args: List[int]):
    if args[0]=='on':
       dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo1))
    elif args[0]=='off':
        dispatcher.remove_handler(MessageHandler(Filters.text & ~Filters.command, echo1))
    else:
        update.effective_message.reply_text('Sorry to say But this is an error')
@run_async
def wspr(bot: Bot, update: Update, args: List[int]):
    event =update
    wwwspr = event.pattern_match.group(1)
    botusername = "@whisperBot"
    if event.reply_to_msg_id:
        event.get_reply_message()
    tap = bot.inline_query(botusername, wwwspr)
    tap[0].click(event.chat_id)
    event.delete()
@run_async
def quickscope(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        bot.kick_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted banning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
def quickunban(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        bot.unban_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted unbanning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)



@run_async
def duck(bot: Bot, update: Update, args: List[int]):
    if args:
        argstr='+'.join(args)
        sample_url = "https://duckduckgo.com/?q={}".format(argstr)
        if sample_url:
            link = sample_url.rstrip()
            update.effective_message.reply_text("Let me 🦆 DuckDuckGo that for you:\n🔎 [{}]({})".format(args[0], link))
        else:
            update.effective_message.reply_text("something is wrong. please try again later.")


@run_async
def youtube(bot: Bot, update: Update, args: List[int]):
    if args:
        argstr='+'.join(args)
        sample_url = "https://m.youtube.com/results?search_query={}".format(argstr)
        if sample_url:
            link = sample_url.rstrip()
            update.effective_message.reply_text("Let me Search In Youtube for you:\n🔎 [{}]({})".format(args[0], link))
        else:
            update.effective_message.reply_text("something is wrong. please try again later.")



@run_async
def anime(bot: Bot, update: Update, args: List[int]):
    if args:
        name = str(args)
        search = AnimeSearch(name) # Search for
        title=search.results[0].title
        genre=search.results[0].type
        sym=search.results[0].synopsis
        rate=search.results[0].score
        url=search.results[0].url
        rep1 = rep.format(title=title, genre=genre, sym=sym, rate=rate, url=url)
        update.effective_message.reply_text(rep1)
    else:
        update.effective_message.reply_text("Somethig wrong")


@run_async
def google(bot: Bot, update: Update, args: List[int]):
    if args:
        argstr='+'.join(args)
        sample_url = "https://google.com/search?q={}".format(argstr)
        if sample_url:
            link = sample_url.rstrip()
            update.effective_message.reply_text("Let me google that for you:\n🔎 [{}]({})".format(args[0], link))
        else:
            update.effective_message.reply_text("something is wrong. please try again later.")



@run_async
def banall(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[0])
        all_mems = sql.get_chat_members(chat_id)
    else:
        chat_id = str(update.effective_chat.id)
        all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            bot.kick_chat_member(chat_id, mems.user)
            update.effective_message.reply_text("Tried banning " + str(mems.user))
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(excp.message + " " + str(mems.user))
            continue


@run_async
def snipe(bot: Bot, update: Update, args: List[str]):
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text("Couldn't send the message. Perhaps I'm not part of that group?")


@run_async
@bot_admin
def getlink(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat")
    chat = bot.getChat(chat_id)
    bot_member = chat.get_member(bot.id)
    if bot_member.can_invite_users:
        invitelink = bot.get_chat(chat_id).invite_link
        update.effective_message.reply_text(invitelink)
    else:
        update.effective_message.reply_text("I don't have access to the invite link!")


@bot_admin
def leavechat(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
        bot.leaveChat(chat_id)
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat")

import urllib.request

from bs4 import BeautifulSoup
@run_async

def cricket(bot: Bot, update: Update, args: List[int]):
    score_page = "http://static.cricinfo.com/rss/livescores.xml"
    page = urllib.request.urlopen(score_page)
    soup = BeautifulSoup(page, "html.parser")
    result = soup.find_all("description")
    Sed = ""
    for match in result:
        Sed += match.get_text() + "\n\n"
    update.effective_message.reply_text(Sed)


@run_async
def search(bot: Bot, update: Update, args: List[int]):
    try:
        movie_name =args
        remove_space = movie_name
        final_name = "+".join(remove_space)
        page = requests.get(
            "https://www.imdb.com/find?ref_=nv_sr_fn&q=" + final_name + "&s=all"
        )
        str(page.status_code)
        soup = bs4.BeautifulSoup(page.content, "lxml")
        odds = soup.findAll("tr", "odd")
        mov_title = odds[0].findNext("td").findNext("td").text
        mov_link = (
            "http://www.imdb.com/" + odds[0].findNext("td").findNext("td").a["href"]
        )
        page1 = requests.get(mov_link)
        soup = bs4.BeautifulSoup(page1.content, "lxml")
        if soup.find("div", "poster"):
            poster = soup.find("div", "poster").img["src"]
        else:
            poster = ""
        if soup.find("div", "title_wrapper"):
            pg = soup.find("div", "title_wrapper").findNext("div").text
            mov_details = re.sub(r"\s+", " ", pg)
        else:
            mov_details = ""
        credits = soup.findAll("div", "credit_summary_item")
        if len(credits) == 1:
            director = credits[0].a.text
            writer = "Not available"
            stars = "Not available"
        elif len(credits) > 2:
            director = credits[0].a.text
            writer = credits[1].a.text
            actors = []
            for x in credits[2].findAll("a"):
                actors.append(x.text)
            actors.pop()
            stars = actors[0] + "," + actors[1] + "," + actors[2]
        else:
            director = credits[0].a.text
            writer = "Not available"
            actors = []
            for x in credits[1].findAll("a"):
                actors.append(x.text)
            actors.pop()
            stars = actors[0] + "," + actors[1] + "," + actors[2]
        if soup.find("div", "inline canwrap"):
            story_line = soup.find("div", "inline canwrap").findAll("p")[0].text
        else:
            story_line = "Not available"
        info = soup.findAll("div", "txt-block")
        if info:
            mov_country = []
            mov_language = []
            for node in info:
                a = node.findAll("a")
                for i in a:
                    if "country_of_origin" in i["href"]:
                        mov_country.append(i.text)
                    elif "primary_language" in i["href"]:
                        mov_language.append(i.text)
        if soup.findAll("div", "ratingValue"):
            for r in soup.findAll("div", "ratingValue"):
                mov_rating = r.strong["title"]
        else:
            mov_rating = "Not available"
        rep1="""
            {mov_title}
Rating : {mov_rating}
Url: {mov_link}
        """
        rep1=rep1.format(mov_title=mov_title,mov_rating=mov_rating,mov_link=mov_link)
        update.effective_message.reply_text(rep1)
    except IndexError:
        update.effective_message.reply_text("Please enter a Valid movie name")



    
@run_async
def imdb(bot: Bot, update: Update, args: List[int]):
    try:
        movie_name =args
        remove_space = movie_name
        final_name = "+".join(remove_space)
        page = requests.get(
            "https://www.imdb.com/find?ref_=nv_sr_fn&q=" + final_name + "&s=all"
        )
        str(page.status_code)
        soup = bs4.BeautifulSoup(page.content, "lxml")
        odds = soup.findAll("tr", "odd")
        mov_title = odds[0].findNext("td").findNext("td").text
        mov_link = (
            "http://www.imdb.com/" + odds[0].findNext("td").findNext("td").a["href"]
        )
        page1 = requests.get(mov_link)
        soup = bs4.BeautifulSoup(page1.content, "lxml")
        if soup.find("div", "poster"):
            poster = soup.find("div", "poster").img["src"]
        else:
            poster = ""
        if soup.find("div", "title_wrapper"):
            pg = soup.find("div", "title_wrapper").findNext("div").text
            mov_details = re.sub(r"\s+", " ", pg)
        else:
            mov_details = ""
        credits = soup.findAll("div", "credit_summary_item")
        if len(credits) == 1:
            director = credits[0].a.text
            writer = "Not available"
            stars = "Not available"
        elif len(credits) > 2:
            director = credits[0].a.text
            writer = credits[1].a.text
            actors = []
            for x in credits[2].findAll("a"):
                actors.append(x.text)
            actors.pop()
            stars = actors[0] + "," + actors[1] + "," + actors[2]
        else:
            director = credits[0].a.text
            writer = "Not available"
            actors = []
            for x in credits[1].findAll("a"):
                actors.append(x.text)
            actors.pop()
            stars = actors[0] + "," + actors[1] + "," + actors[2]
        if soup.find("div", "inline canwrap"):
            story_line = soup.find("div", "inline canwrap").findAll("p")[0].text
        else:
            story_line = "Not available"
        info = soup.findAll("div", "txt-block")
        if info:
            mov_country = []
            mov_language = []
            for node in info:
                a = node.findAll("a")
                for i in a:
                    if "country_of_origin" in i["href"]:
                        mov_country.append(i.text)
                    elif "primary_language" in i["href"]:
                        mov_language.append(i.text)
        if soup.findAll("div", "ratingValue"):
            for r in soup.findAll("div", "ratingValue"):
                mov_rating = r.strong["title"]
        else:
            mov_rating = "Not available"
        rep1="""
            {mov_title}
Rating : {mov_rating}
Url: {mov_link}
        """
        rep1=rep1.format(mov_title=mov_title,mov_rating=mov_rating,mov_link=mov_link)
        update.effective_message.reply_text(rep1)
    except IndexError:
        update.effective_message.reply_text("Please enter a Valid movie name")



__help__ = """
**Owner only:**
- /getlink **chatid**: Get the invite link for a specific chat.
- /banall: Ban all members from a chat
- /leavechat **chatid** : leave a chat
**Sudo/owner only:**
- /quickscope **userid** **chatid**: Ban user from chat.
- /quickunban **userid** **chatid**: Unban user from chat.
- /snipe **chatid** **string**: Make me send a message to a specific chat.
- /rban **userid** **chatid** remotely ban a user from a chat
- /runban **userid** **chatid** remotely unban a user from a chat
- /Stats: check bot's stats
- /chatlist: get chatlist
- /gbanlist: get gbanned users list
- /gmutelist: get gmuted users list
- Chat bans via /restrict chat_id and /unrestrict chat_id commands
**Support user:**
- /Gban : Global ban a user
- /Ungban : Ungban a user
- /Gmute : Gmute a user
- /Ungmute : Ungmute a user
Sudo/owner can use these commands too.
**Users:**
- /anime Search Animes
- /listsudo Gives a list of sudo users
- /listsupport gives a list of support users
"""
__mod_name__ = "Special"

SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
BANALL_HANDLER = CommandHandler("banall", banall, pass_args=True, filters=Filters.user(OWNER_ID))
QUICKSCOPE_HANDLER = CommandHandler("quickscope", quickscope, pass_args=True, filters=CustomFilters.sudo_filter)
QUICKUNBAN_HANDLER = CommandHandler("quickunban", quickunban, pass_args=True, filters=CustomFilters.sudo_filter)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
LEAVECHAT_HANDLER = CommandHandler("leavechat", leavechat, pass_args=True, filters=Filters.user(OWNER_ID))
ANIME_HANDLER = CommandHandler("anime", anime,pass_args=True)
DUCK_HANDLER = CommandHandler("duck", duck,pass_args=True)
GOOGLE_HANDLER = CommandHandler("google", google,pass_args=True)
YOUTUBE_HANDLER = CommandHandler("youtube", youtube,pass_args=True)
CRICKET_HANDLER = CommandHandler("cricket", cricket,pass_args=True)
SEARCH_HANDLER = CommandHandler("search", search,pass_args=True)
IMDB_HANDLER = CommandHandler("imdb", imdb,pass_args=True)
WSPR_HANDLER = CommandHandler("wspr", wspr,pass_args=True)
ECHO_HANDLER = CommandHandler("echo", echo,pass_args=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(IMDB_HANDLER)
dispatcher.add_handler(ANIME_HANDLER)
dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(BANALL_HANDLER)
dispatcher.add_handler(QUICKSCOPE_HANDLER)
dispatcher.add_handler(QUICKUNBAN_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(LEAVECHAT_HANDLER)
dispatcher.add_handler(DUCK_HANDLER)
dispatcher.add_handler(GOOGLE_HANDLER)
dispatcher.add_handler(YOUTUBE_HANDLER)
dispatcher.add_handler(CRICKET_HANDLER)
dispatcher.add_handler(SEARCH_HANDLER)
dispatcher.add_handler(WSPR_HANDLER)



