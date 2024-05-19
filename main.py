import asyncio
import os
import dataset
import dotenv
import hikari
import lightbulb
from logging import info
from shopify import Shopify
from monitoring import monitor_site, monitor_collection

dotenv.load_dotenv()

db = dataset.connect("sqlite:///data.db")
bot = lightbulb.BotApp(token=os.getenv("TOKEN"))
bot.d.monitors = db["monitors"]
bot.d.images = db["images"]


async def run_background() ->    None:
    info("Scraper started.")

    while True:
        for monitor in bot.d.monitors:
            info(
                "Monitoring {type} URL: {url}".format(
                    type=monitor["type"],
                    url=monitor["url"],
                )
            )

            try:
                if monitor["type"] == "site":
                    await monitor_site(bot, monitor)

                if monitor["type"] == "collection": 
                    await monitor_collection(bot, monitor)

            except Exception as e:
                info("Error while monitoring: {error}".format(error=e))

        await asyncio.sleep(int(os.getenv("INTERVAL", 60)))


@bot.listen(hikari.ShardReadyEvent)
async def ready_listener(_):
    info("Bot is ready")
    asyncio.create_task(run_background())


@bot.command()
@lightbulb.command("monitors", "Manage monitors")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def monitors() -> None:
    pass


@monitors.child
@lightbulb.command("add", "Add a monitor")
@lightbulb.implements(lightbulb.SlashSubGroup)
async def add() -> None:
    pass


@add.child
@lightbulb.option("channel", "Channel", type=hikari.TextableChannel, required=True)
@lightbulb.option("url", "Site URL", type=str, required=True)
@lightbulb.command("site", "Enable monitoring for a site")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def register_site(ctx: lightbulb.Context) -> None:
    if not ctx.options.url.startswith(("https://", "http://")):
        await ctx.respond("❌ Invalid URL")
        return

    config = Shopify.get_shopify_config(ctx.options.url)

    if config is not None:
        ctx.bot.d.monitors.insert(
            {
                "url": ctx.options.url,
                "channel_id": ctx.options.channel.id,
                "type": "site",

            }
        )
        await ctx.respond("✅ Registered site monitoring!")
        return

    await ctx.respond("❌ This website is not a Shopify website")


@add.child
@lightbulb.option("channel", "Channel", type=hikari.TextableChannel, required=True)
@lightbulb.option("url", "Collection URL", type=str, required=True)
@lightbulb.command("collection", "Enable monitoring for a collection")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def register_collection(ctx: lightbulb.Context) -> None:
    if not ctx.options.url.startswith(("https://", "http://")):
        await ctx.respond("❌ Invalid URL")
        return

    config = Shopify.get_shopify_config(ctx.options.url)

    if config is None:
        await ctx.respond("❌ This website is not a Shopify website")
        return

    if Shopify.is_collection(ctx.options.url):
        ctx.bot.d.monitors.insert(
            {
                "url": ctx.options.url,
                "channel_id": ctx.options.channel.id,
                "type": "collection",
            }
        )
        await ctx.respond("✅ Registered collection monitoring!")
        return

    await ctx.respond("❌ The URL is invalid, it should contains /collections/.")


@monitors.child
@lightbulb.option("channel", "Channel", type=hikari.TextableChannel, required=True)
@lightbulb.command("list", "List monitors")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def list(ctx: lightbulb.Context):
    monitors = bot.d.monitors.find(channel_id=ctx.options.channel.id)

    if not monitors:
        await ctx.respond("❌ No monitors found")
        return

    for monitor in monitors:
        embed = hikari.Embed()
        embed.title = "Monitor #{}".format(monitor["id"])
        embed.add_field("URL", monitor["url"], inline=True)
        embed.add_field("Type", str(monitor["type"]).capitalize(), inline=True)
 
        image_count = bot.d.images.count(monitor_id=monitor["id"])
        embed.add_field("Images found", image_count, inline=True)
        await ctx.respond(embed=embed)
        

@monitors.child
@lightbulb.option("id", "Monitor ID", type=int, required=True)
@lightbulb.command("remove", "Remove a monitor")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def remove(ctx: lightbulb.Context):
    monitor = bot.d.monitors.find_one(id=ctx.options.id)

    if not monitor:
        await ctx.respond("❌ Monitor not found")
        return

    bot.d.monitors.delete(id=ctx.options.id)
    await ctx.respond("✅ Monitor removed")


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot.run(
        activity=hikari.Activity(
            name="Shopify websites!", type=hikari.ActivityType.WATCHING
        ),
    )
