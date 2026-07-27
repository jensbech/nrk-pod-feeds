import os
import json

from datetime import datetime
from common.helpers import *

def test_write_feeds_file():
    feeds_file = "tests/feeds.js"
    os.makedirs("tests/", exist_ok=True)

    podcasts = [{
        "id": "kongerekka",
        "title": "De 10 siste fra Kongerekka",
        "season": "LATEST_SEASON",
        "enabled": "true"
    }]

    if os.path.exists(feeds_file):
        os.remove(feeds_file)
    write_feeds_file(feeds_file, podcasts)
    saved = open(feeds_file, "r")
    str = saved.read()
    saved.close()

    assert str

def test_write_feeds_file_with_images():
    feeds_file = "tests/feeds_images.js"
    feeds_dir = "tests/rss_unit"
    image_url = "https://gfx.nrk.no/example.jpg"
    os.makedirs(feeds_dir, exist_ok=True)

    xml = (
        "<?xml version='1.0' encoding='UTF-8'?>"
        "<rss xmlns:itunes=\"http://www.itunes.com/dtds/podcast-1.0.dtd\" version=\"2.0\">"
        "<channel><title>Kongerekka</title>"
        f"<itunes:image href=\"{image_url}\"/>"
        "</channel></rss>"
    )
    with open(f"{feeds_dir}/kongerekka.xml", "w") as f:
        f.write(xml)

    podcasts = [
        {
            "id": "kongerekka",
            "title": "Kongerekka",
            "season": "LATEST_SEASON",
            "enabled": True
        },
        {
            "id": "finnes_ikke",
            "title": "Finnes ikke",
            "season": None,
            "enabled": False
        }
    ]

    write_feeds_file(feeds_file, podcasts, feeds_dir)

    with open(feeds_file, "r") as f:
        content = f.read()

    entries = json.loads(content.removeprefix("const feeds = "))
    assert entries[0]["image"] == image_url
    assert "image" not in entries[1]

def test_get_feed_image_missing():
    assert get_feed_image("tests/rss_unit", "finnes_ikke") == None

def test_write_podcasts_changelog():
    file = "tests/DISCOVERY_UNIT.md"
    os.makedirs("tests/", exist_ok=True)

    today = datetime.now()
    ch_date = today.date()

    if os.path.exists(file):
        os.remove(file)

    old_changes = [
        "Added podcast foo",
        "Deprecated podcast bar"
    ]

    new_changes = [
        "Added podcast foobar",
        "Deprecated podcast barfoo"
    ]

    write_podcasts_changelog(file, today, old_changes)
    write_podcasts_changelog(file, today, new_changes)

    saved = open(file, "r")
    str = saved.read()
    saved.close()

    expected = f"""# Podcast Discovery Changelog  
### {ch_date}  
- Added podcast foobar  
- Deprecated podcast barfoo  
### {ch_date}  
- Added podcast foo  
- Deprecated podcast bar  
"""

    assert str == expected

def test_get_podcasts_config():
    podcasts_cfg_file = "podcasts.json"
    with open(podcasts_cfg_file, 'r') as file:
        data = file.read()
        
    assert json.loads(data)