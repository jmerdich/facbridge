import asyncio
import re
import time
import os
import logging
from os.path import dirname

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import discord
from discord.ext import commands

from mcrcon import MCRcon

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

class FacLogHandler(PatternMatchingEventHandler):
    def __init__(self, fbot, logfile):
        self.fbot = fbot
        self.log_loc = logfile
        self.logfile = None

        super().__init__([logfile])
        self.spin_up()
        self.observer = Observer()
        self.observer.schedule(self, dirname(self.log_loc), recursive=False)
        self.observer.start()

    def spin_up(self):
        self.logfile = None
        elapsed = 0
        while self.logfile is None:
            try:
                self.logfile = open(self.log_loc, 'r')
            except:
                time.sleep(1)
                if elapsed > 20:
                    raise Exception("Timed out opening log file!")

        # read up to last line before EOF
        for line in self.logfile:
            pass

    def on_modified(self, event):
        for line in self.logfile:
            m = re.match("^[-0-9: ]+\[([A-Z]+)\] (.+)$", line)
            if m is None:
                continue
            dispatch = {
                "CHAT": self.got_chat
                }

            method = dispatch.get(m.group(1), None)

            if method is not None:
                method(m.group(2))
            else:
                self.default_handler(m.group(1), m.group(2))

    def default_handler(self, kind, text):
        logger.debug("Factorio sent unknown '%s': '%s'", kind, text)
        channel = self.fbot.get_channel(self.fbot.bridge_id)
        coro = channel.send(text)
        asyncio.run_coroutine_threadsafe(coro, self.fbot.loop)

    def got_chat(self, text):
        logger.debug("Factorio sent CHAT '%s'", text)
        user, msg = text.split(": ", 1)
        if user == "<server>":
            return

        channel = self.fbot.get_channel(self.fbot.bridge_id)
        coro = channel.send(text)
        asyncio.run_coroutine_threadsafe(coro, self.fbot.loop)

class FacBot(commands.Bot):
    def __init__(self, bridge_id, data_dir, host):
        super().__init__(['/', ''])
        self.bridge_id = int(bridge_id)
        self.data_dir = data_dir
        self.host = host
        with open(data_dir + "/config/rconpw", "r") as f:
            self.pw = f.readline().strip()
        self.log_in = FacLogHandler(self, data_dir + "/factorio-current.log")


    async def on_message(self, message):
        if message.author.bot:
            return # don't listen to other bots....
        ctx = await self.get_context(message)

        if ctx.prefix == '/':
            # an actual command
            return await self.invoke(ctx)
        elif ctx.channel.id == self.bridge_id:
            return await self.send_to_factorio(ctx)

    async def send_to_factorio(self, ctx):
        msg = "{}: {}".format(ctx.author.display_name, ctx.message.content)
        logger.debug("Msg from discord: \"{}\"".format(msg))
        with MCRcon(self.pw, self.pw, 27015) as rcon:
            resp = rcon.command(msg)
            print(resp)

    async def on_ready(self):
        logger.info("Connected to discord")
    
if __name__ == "__main__":
    print("Starting discord/factorio bridge....")
    fb = FacBot(os.environ['CHANNEL_ID'],
                os.environ["FACTORIO_DATA_DIR_PATH"],
                os.environ.get("FACTORIO_HOST", '127.0.0.1'))
    fb.run(os.environ["DISCORD_KEY"])


