from hikari import Embed, Color
from urllib.parse import urlparse, urljoin


def generate_product_embed(
    monitor: dict, product: dict, image: dict, type: str, provider: str
) -> Embed:
    url = urlparse(monitor["url"])

    embed = Embed(title=product["title"], url=product["url"])
    embed.set_author(
        name=url.hostname,
        url=monitor["url"],
        icon="https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={}&size=256".format(
            urljoin(monitor["url"], "/")
        ),
    )

    embed.set_image(image["src"])
    embed.add_field(name="Brand", value=product["brand"], inline=True)
    embed.add_field(name="Resolution", value=str(str(image["height"]) + "x" + str(image["width"])), inline=True)
    embed.add_field(name="Position", value=image["position"], inline=True)
    embed.add_field(name="Created At", value=image["created_at"], inline=True)
    
  
    if type == "new":
        embed.color = Color(0xA1C181)
        embed.set_footer(text="🆕 New image")
    elif type == "update":
        embed.color = Color(0xFE7F2D)
        embed.set_footer(text="🔄 Image updated")


    if provider == "collection":
        embed.set_footer(text=f"{embed.footer.text} | 📦 Collection monitoring")
    elif provider == "site":
        embed.set_footer(text=f"{embed.footer.text} | 📦 Site monitoring")

    return embed