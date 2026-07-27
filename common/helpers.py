import os
import logging
import json
import xml.etree.ElementTree as ET

def init():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)

ITUNES_NS = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"

def get_last_feed(feeds_dir, podcast_id):
    try:
        path = f"{feeds_dir}/{podcast_id}.xml"
        tree = ET.parse(path)
        root = tree.getroot()
        return root
    except:
        logging.info(f"No existing feed found for podcast {podcast_id}")
        return None

def get_podcasts_config(podcasts_cfg_file):
    with open(podcasts_cfg_file, 'r') as file:
        data = file.read()
        return json.loads(data)

def write_podcasts_config(config_file, podcasts):
    f = open(config_file, "w")
    str = json.dumps(podcasts, ensure_ascii=False, indent=4)
    f.write(str)
    f.close()
    
    logging.info(f"Podcasts config written to file: {config_file}")

def get_feed_image(feeds_dir, podcast_id):
    feed = get_last_feed(feeds_dir, podcast_id)
    if feed is None:
        return None

    image = feed.find(f"channel/{ITUNES_NS}image")
    if image is None:
        return None

    return image.get("href")

def write_feeds_file(feeds_file, podcasts, feeds_dir=None):
    entries = []
    for podcast in podcasts:
        entry = dict(podcast)
        if feeds_dir:
            image = get_feed_image(feeds_dir, podcast["id"])
            if image:
                entry["image"] = image
        entries.append(entry)

    f = open(feeds_file, "w")
    str = json.dumps(entries, ensure_ascii=False, indent=2)
    f.write(f"const feeds = {str}")
    f.close()

    logging.info(f"Podcast feeds written to file: {feeds_file}")

def write_podcasts_changelog(file, date, changes):
    if len(changes) == 0:
        return
    
    header = "# Podcast Discovery Changelog  "
    sub_header = f"### {date.date()}  "
    existing = ""
    
    if os.path.exists(file):
        fr = open(file, "r")
        existing_lines = fr.readlines()[1:]
        existing = "".join(existing_lines)
        fr.close()

    f = open(file, "w")
    new = "  \n- ".join(changes)
    f.write(f"{header}\n{sub_header}\n- {new}  \n{existing}")
    f.close()
    
    logging.info(f"Podcast config changelog written to file: {file}")

def get_version():
    with open("version.txt") as file:
        return file.read()
