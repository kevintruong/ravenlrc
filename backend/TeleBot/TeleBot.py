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
import sqlite3
from telegram import Bot, Chat
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import backend.yclogger
from backend.TeleBot.TeleCmder import TeleBuildCmder

telelog = logging.getLogger('telebot')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

elinkTeleUserDb = None

DEFAULT_DB = os.path.join(os.path.dirname(__file__), 'ytcreator.sqlite3')
YtCreator_BotToken = "698566319:AAHnZBx4LK4um0jHhxMINTWrUuwvb_wLFbk"
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
            YtCreatorBot.sendMessage(chat_id=user.id, text="{} {} already added".format(user.first_name,
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
    bot = None
    elinkbot = None

    def __init__(self):
        self.testcases = []
        pass

    def get_testcases(self):
        return self.testcases

    @classmethod
    def get_elinkbot(cls):
        if YtCreatorTeleBotManager.elinkbot is None:
            YtCreatorTeleBotManager.elinkbot = YtCreatorTeleBotManager()
        return YtCreatorTeleBotManager.elinkbot

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

    @classmethod
    def build(cls, bot: bot, update):
        print(update.message.text)
        buildcmd = update.message.text
        try:
            buildcmder = TeleBuildCmder(buildcmd)
            output = buildcmder.run_build_cmd()
            update.message.reply_text('Build Complete {}'.format(output))
        except Exception as exp:
            update.message.reply_text('Build error {}'.format(exp))

    @classmethod
    def echo(cls, bot: Bot, update):
        """Echo the user message."""
        update.message.reply_text(update.message.text)
        bot.sendMessage(chat_id=update.message.chat.id, text='hello')

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
        global YtCreatorBot
        ytBot = YtCreatorBot
        if ytBot is None:
            ytBot = Bot(YtCreator_BotToken)
            YtCreatorBot = ytBot

        updater = Updater(bot=ytBot)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", YtCreatorTeleBotManager.start))
        dp.add_handler(CommandHandler("help", YtCreatorTeleBotManager.help))
        dp.add_handler(CommandHandler("build", YtCreatorTeleBotManager.build))

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


if __name__ == '__main__':
    telelog.info("hello ")
    YtCreatorTeleBotManager.TeleNotifier_Runner()
#
#
# if eLinkGateBot is None:
#     executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
#     loop = asyncio.get_event_loop()
#     entry = loop.run_in_executor(executor, TeleNotifier_Runner)
#     # TeleNotifier_Runner()
