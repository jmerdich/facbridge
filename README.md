Bidirectional bridge between factorio chat and a Discord channel

This basically works by (1) scraping Factorio's log file and sending chat messages to discord and (2) relaying non-command discord messages on a particular channel to factorio via RCON.

| Environment Variable     | Default   | Info                                                                                        |
|--------------------------|-----------|---------------------------------------------------------------------------------------------|
| `FACTORIO_DATA_DIR_PATH` | n/a       | Path to the factorio data directory, used to scrape the logs and get the RCON password      |
| `FACTORIO_HOST`          | 127.0.0.1 | Internal host/ip of the factorio server, used to connect via RCON.                          |
| `DISCORD_KEY`            | n/a       | API key for the discord bot                                                                 |
| `CHANNEL_ID`             | n/a       | Channel ID for the bot to relay messages to. The bot will accept commands from any channel. |

Requires factorio data directory mapped at a location specified by the `FACTORIO_DATA_DIR_PATH` env variable and the `--console-log $FACTORIO_DATA_DIR_PATH/factorio-current.log` option on the host at `FACTORIO_HOST`.

Also needs a `DISCORD_KEY` and `CHANNEL_ID`. To, you know, talk to discord.
