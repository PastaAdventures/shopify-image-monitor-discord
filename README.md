# Shopify Image Monitor for Discord

Shopify Image Monitor for Discord is a Python-based project that allows users to track changes in images for any Shopify site or collections. It provides low latency notifications to Discord channels, ensuring you never miss an important change.

## Features

- Monitor for new product images for any Shopify site or collection
- Sends notifications to a specified Discord channel.
- Fully configurable to track as many sites/collections as desired.

## Bot commands

```sh
/monitors add site [url] [channel]              # Monitor a product
/monitors add collection [url] [channel]        # Monitor a collection
/monitors list [channel]                        # List active monitors for a given channel
/monitors remove [id]                           # Deactivate a monitor
```

## Requirements

- Python 3.11 or later
- Discord account and server

## Installation

1. Clone this repository
2. Install requirements and Python dependencies (`pip install -r requirements.txt`)
3. Copy the .env.example to .env and define your configuration
4. Run the project using `python -OO main.py`

> You'll need to setup a Discord bot with the `bot` scope and following permissions:
>
> - Send messages
> - Use Slash Commands
> - Read Messages/View Channels

## Drawbacks and limitations

- I haven't tested this bot on password-protected websites, this will certainly result in an error.
- No proxy-system included, use latency like 3-5 minutes to avoid bans.
