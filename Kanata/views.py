from abcli import string
from browser import html
from ..utils import *
from abcli import logging
import logging

logger = logging.getLogger(__name__)


def view_Kanata(request):
    return render(
        request,
        "item.html",
        {
            "abcli_fullname": fullname(),
            "autorefresh": 300,
            "description": add_urls(
                {
                    "version": Kanata.version,
                    '<a href="/tag/Kanata_video_id_{}">video_id</a>'.format(
                        Kanata.version
                    ): jobs.flow(
                        "Kanata_video_id_{}".format(Kanata.version),
                        "Kanata_worker",
                    ),
                    '<a href="/tag/Kanata_slice_{},work">slice</a>'.format(
                        Kanata.version
                    ): jobs.flow("Kanata_slice_{},work".format(Kanata.version)),
                    "faces": jobs.state(
                        "Kanata_slice_{},face_finder,track".format(Kanata.version)
                    ),
                    "videos": jobs.state(
                        "Kanata_render_{},video".format(Kanata.version)
                    ),
                    "last update": string.pretty_date(),
                }
            ),
            "title_postfix": "Kanata",
        },
    )


def view_live(request):
    from Kanata import live

    return render(
        request,
        "item.html",
        {
            "abcli_fullname": fullname(),
            "autorefresh": 300,
            "description": add_urls(
                {
                    "version": live.version,
                    '<a href="/tag/live_eye">live_eye</a>': jobs.flow(
                        "live_eye",
                        "live_worker_{}".format(live.version),
                    ),
                    # '<a href="/tag/live_slice_{},work">slice</a>'.format(
                    #    live.version
                    # ): jobs.flow("live_slice_{},work".format(live.version)),
                    # "faces": jobs.state(
                    #    "live_slice_{},face_finder,track".format(live.version)
                    # ),
                    # "videos": jobs.state("live_render_{},video".format(live.version)),
                    "last update": string.pretty_date(),
                }
            ),
            "title_postfix": "live",
        },
    )


def view_youtube_video_id(object, page, item_per_page):
    return (
        {
            "description": {
                "object": object,
                "tags": tags.get(object),
                "youtube": f'<a href="https://www.youtube.com/watch?v={object}">{object}</a>',
            },
            "items_n_urls": zip([], []),
            "title_postfix": " | ".join(["youtube_video_id", object]),
            f"content": '<iframe width="560"  height="315" src="https://www.youtube.com/embed/{object}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
        },
        {"template_name": "item.html"},
    )
