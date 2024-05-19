from lightbulb import BotApp
from shopify import Shopify
from logging import info
from embed import generate_product_embed
from datetime import datetime
import pprint
import json


async def check_product(
    bot: BotApp, monitor: dict, product: dict, provider: str
) -> None:
    type = "new"
    announce = False
    for image in product["images"]:
        saved_image = bot.d.images.find_one(
            monitor_id=monitor["id"], product_id=product["id"], image_id=image["id"]
        )

        if saved_image is None:
            info("New image detected: {id}".format(id=image["id"]))

            bot.d.images.insert(
                {
                    "monitor_id": monitor["id"],
                    "product_id": product["id"],
                    "image_id": image["id"],
                    "available": image["available"],
                    "created_at": datetime.now().timestamp(),
                    "updated_at": datetime.now().timestamp(),
                }
            )

            type = "new"
            announce = True
        elif bool(saved_image["available"]) != bool(image["available"]) or int(
            saved_image["image_id"]
        ) != int(image["id"]):
            info("Changes detected for image {id}".format(id=image["id"]))

            bot.d.images.update(
                {
                    "monitor_id": monitor["id"],
                    "product_id": product["id"],
                    "image_id": image["id"],
                    "available": image["available"],
                    "updated_at": datetime.now().timestamp(),
                },
                ["monitor_id", "product_id", "image_id"],
            )

            type = "update"
            announce = True
        else:
            info("No changes detected for image {id}".format(id=image["id"]))

    if announce:
        for image in product["images"]:
            embed = generate_product_embed(monitor, product, image=image, type=type, provider=provider)
            await bot.rest.create_message(monitor["channel_id"], embed=embed)


async def monitor_site(bot: BotApp, monitor: dict) -> None:
    products = Shopify.get_products(monitor["url"])

    for product in products:
        await check_product(bot, monitor, product, "site")


async def monitor_collection(bot: BotApp, monitor: dict) -> None:
    products = Shopify.get_products(monitor["url"])

    for product in products:
        await check_product(bot, monitor, product, "collection")
