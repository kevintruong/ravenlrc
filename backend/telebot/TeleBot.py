# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import os
import re
import sqlite3
import threading

from telegram import Bot, Chat, Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

from backend.storage.gdrive import GDriveMnger
from backend.storage.gsheet import GoogleSheetStream
from backend.telebot.TeleCmder import TeleBuildCmder, TelePublishCmder

from backend.yclogger import telelog

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

elinkTeleUserDb = None

DEFAULT_DB = os.path.join(os.path.dirname(__file__), 'ytcreator.sqlite3')
YtCreator_BotToken = "698566319:AAHnZBx4LK4um0jHhxMINTWrUuwvb_wLFbk"
# YtCreator_BotToken = "714001436:AAHJ54DYwZeTHAPhjFagVPKeG61nURx7GI8"  # DEBUG at local
YtCreatorBuildChannel = -1384364301

YtCreatorBuildChannelId = -379811995  # test
# YtCreatorBuildChannelId = -1001124531239
YtCreatorBot = None


class TeleRegisterUserDb:
    tele_reg_user_db = None

    def create_debug_db(self, dbfile=DEFAULT_DB):
        self.dbfile = dbfile
        self.debugdbconn = sqlite3.connect(dbfile)
        sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS TeleRegisteredUser (
                                            id integer primary key ,
                                            type text,
                                            username text ,
                                            first_name text  ,
                                            last_name text 
                                        );"""
        cur = self.debugdbconn.cursor()
        cur.execute(sql_create_tasks_table)
        self.debugdbconn.commit()

    @classmethod
    def get_teleRegisteredUserDb(cls, dbfile=DEFAULT_DB):
        if TeleRegisterUserDb.tele_reg_user_db is None:
            TeleRegisterUserDb.tele_reg_user_db = TeleRegisterUserDb(dbfile)
            return TeleRegisterUserDb.tele_reg_user_db
        else:
            return TeleRegisterUserDb.tele_reg_user_db

    def __init__(self, dbfile):
        self.dbfile = None
        self.debugdbconn = None
        self.create_debug_db(dbfile)
        pass

    def get_userid(self, userid):
        debugdb = sqlite3.connect(self.dbfile)
        cur = debugdb.cursor()
        cur.execute('select * from TeleRegisteredUser where id=? ', (userid,))
        rows = cur.fetchall()
        debugdb.close()
        if len(rows) == 0:
            return None
        return rows

    def add_userid(self, user: Chat):
        """
                                            id integer primary key ,
                                            type text,
                                            username text NOT NULL,
                                            first_name text  NOT NULL,
                                            last_name text NOT NULL,
        :param user:
        :return:
        """
        curuser = self.get_userid(user.id)
        if curuser is not None:
            print("{} allready existed".format(user.username))
            YtCreatorBot.sendMessage(chat_id=user.id,
                                     text="{} {} already added".format(user.first_name,
                                                                       user.last_name))
            return
        else:
            self.debugdbconn = sqlite3.connect(self.dbfile)
            cur = self.debugdbconn.cursor()
            print("insert new record")
            cur.execute(
                "insert into TeleRegisteredUser (id,type,username,first_name,last_name) values(?,?,?,?,?)",
                (user.id, user.type, str(user.username), user.first_name, user.last_name))
            self.debugdbconn.commit()
            self.debugdbconn.close()
            pass

    def get_all_userid(self):
        debugdb = sqlite3.connect(self.dbfile)
        cur = debugdb.cursor()
        cur.execute('select * from TeleRegisteredUser')
        rows = cur.fetchall()
        debugdb.close()
        userids = []
        for each in rows:
            userids.append(each[0])
        return userids


class TeleNotifyStream(logging.Handler):
    instance = None

    def __init__(self, level=logging.NOTSET):
        global YtCreatorBot
        global elinkTeleUserDb
        super().__init__(level=logging.DEBUG)
        self.userdb = TeleRegisterUserDb.get_teleRegisteredUserDb()
        self.YtCreatorBot = Bot(token=YtCreator_BotToken)
        YtCreatorBot = self.YtCreatorBot
        elinkTeleUserDb = self.userdb

    def emit(self, record):
        json = self.format(record)
        update = self.YtCreatorBot.getUpdates()
        for each in self.userdb.get_all_userid():
            self.YtCreatorBot.sendMessage(chat_id=each, text=json)
        self.YtCreatorBot.sendMessage(chat_id=YtCreatorBuildChannelId, text=json)

    @classmethod
    def get_instance(cls):
        return cls.instance


class YtCreatorTeleBotManager:
    input_return = None
    bot: Bot = None
    elinkbot = None
    ytcreatorDriver = None
    gsheetsonginfodb = None
    cur_chat = None
    wait_input_evt = threading.Event()

    GG_INPUT_TOKEN, TYPING_REPLY, TYPING_CHOICE = range(3)

    def __init__(self):
        self.testcases = []
        pass

    def get_testcases(self):
        return self.testcases

    @classmethod
    def get_elinkbot(cls):
        if cls.elinkbot is None:
            cls.elinkbot = YtCreatorTeleBotManager()
        return cls.elinkbot

    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    @classmethod
    def start(cls, bot: Bot, update):
        global elinkTeleUserDb
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')
        db = elinkTeleUserDb
        if db is None:
            db = TeleRegisterUserDb(DEFAULT_DB)
            elinkTeleUserDb = db
        db.add_userid(update.message.chat)

    @classmethod
    def help(cls, bot, update):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')
        update.message.reply_text('/build <configure_file> build type \n '
                                  'example: /build TocGioThoiBay release')
        update.message.reply_text('/build <configure_file> build type \n '
                                  'example: /build TocGioThoiBay release')

    @classmethod
    def wait_for_input(cls):
        cls.wait_input_evt.wait()
        return cls.input_return

    @classmethod
    def authenticate_new_channel(cls, authenticate_url):
        print(authenticate_url)
        cls.bot.sendMessage(cls.cur_chat.id, text=authenticate_url, reply_markup=ForceReply())
        cls.wait_for_input()
        return cls.input_return
        pass

    @classmethod
    def input_token(cls, bot, update):
        update.message.reply_text('Alright, please send me the category first, '
                                  'for example "Most impressive skill"')
        cls.input_return = update.message.text.split()[1]
        cls.wait_input_evt.set()

    @classmethod
    @run_async
    def new(cls, bot: Bot, update):
        """
        register new channel
        :param bot:
        :param update:
        :return:
        """
        cls.cur_chat = update.message.chat
        from backend.publisher.youtube.youtube_uploader import YoutubeUploader
        register_newchannel = update.message.text
        cmd_args = register_newchannel.split()
        channel = cmd_args[1]
        YoutubeUploader(channel, cls.authenticate_new_channel)

    @classmethod
    @run_async
    def build(cls, bot: Bot, update):
        print(update.message.text)
        buildcmd = update.message.text
        try:

            buildcmder = TeleBuildCmder(buildcmd)
            update.message.reply_text('Build {} start'.format(buildcmder.mvconfig))
            output = buildcmder.run_build_cmd()
            update.message.reply_text('Build Complete {}'.format(output))
            # previewfile = YtCreatorTeleBotManager.ytcreatorDriver.generate_html_preview_file(output)
            # if previewfile:
            #     bot.sendDocument(update.message.chat.id, document=open(previewfile, 'rb'))
            # else:
            #     update.message.reply_text('Cannot create preview file, error: Timeout')

        except Exception as exp:
            update.message.reply_text('Build error {}'.format(exp))
            telelog.info(exp)
            raise exp

    @classmethod
    @run_async
    def publish(cls, bot: Bot, update):
        print(update.message.text)
        buildcmd = update.message.text
        try:
            buildcmder = TelePublishCmder(buildcmd)
            update.message.reply_text('publish {} start'.format(buildcmder.cmder.songinfo.title))
            buildcmder.run_publish_cmd()
            update.message.reply_text('publis {} Complete'.format(buildcmder.cmder.songinfo.title))
        except Exception as exp:
            update.message.reply_text('Build error {}'.format(exp))
            telelog.debug(exp)
            raise exp

    @classmethod
    @run_async
    def echo(cls, bot: Bot, update: Update):
        """Echo the user message."""
        try:
            id_sheet = update.message.chat.id
            name = str(update.message.chat.first_name) + str(update.message.chat.last_name) + str(id_sheet)
            message: str = update.message.text
            values = message.split()
            url = values[0]
            if len(values) == 1:
                record = None
            else:
                record = values[1]
            isvalid = cls.url_validate(url)
            if isvalid:
                print("url valid")
                from backend.crawler.nct import SongInfoCrawler
                songinfo = SongInfoCrawler.get_song_info(url)
                if cls.gsheetsonginfodb.emit(songinfo, record):
                    update.message.reply_text(
                        'your song {} already updated to database(googlesheet)'.format(songinfo.title))
                else:
                    update.message.reply_text(
                        'your song {} is duplicated, already existed in database '.format(songinfo.title))

            else:
                update.message.reply_text('Hello, this is your message')
                update.message.reply_text(update.message.text)
        except Exception as exp:
            telelog.debug(exp)
            update.message.reply_text('something wrong error {}'.format(exp))
            raise exp

    @classmethod
    def url_validate(cls, url: str):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        isvalid = re.match(regex, url)
        if isvalid is not None:
            return True
        else:
            return False

    @classmethod
    def error(cls, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    # @classmethod
    # def status(cls, bot, update):
    #     """Log Errors caused by Updates."""
    #     logger.warning('Update "%s" caused error "%s"', update)
    #     update.message.reply_text('current log return !')

    @classmethod
    def TeleNotifier_Runner(cls):
        """Start the bot."""
        # Create the EventHandler and pass it your bot's token.
        cls.bot = Bot(YtCreator_BotToken)
        YtCreatorTeleBotManager.ytcreatorDriver = GDriveMnger()
        YtCreatorTeleBotManager.gsheetsonginfodb = GoogleSheetStream()
        updater = Updater(bot=cls.bot, request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})

        # Get the dispatcher to register handlers
        dp = updater.dispatcher
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", YtCreatorTeleBotManager.start))
        dp.add_handler(CommandHandler("help", YtCreatorTeleBotManager.help))
        dp.add_handler(CommandHandler("build", YtCreatorTeleBotManager.build))
        dp.add_handler(CommandHandler("publish", YtCreatorTeleBotManager.publish))
        dp.add_handler(CommandHandler("new", YtCreatorTeleBotManager.new))
        dp.add_handler(CommandHandler("input", YtCreatorTeleBotManager.input_token))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, YtCreatorTeleBotManager.echo))

        # log all errors
        dp.add_error_handler(YtCreatorTeleBotManager.error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

# if __name__ == '__main__':
#     YtCreatorTeleBotManager.TeleNotifier_Runner()
#
#
# if eLinkGateBot is None:
#     executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
#     loop = asyncio.get_event_loop()
#     entry = loop.run_in_executor(executor, TeleNotifier_Runner)
#     # TeleNotifier_Runner()
