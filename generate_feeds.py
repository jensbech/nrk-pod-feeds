import logging
import re
import random
from podgen import Podcast, Episode, Media
from dateutil import parser
from datetime import timedelta, datetime, timezone

from common.helpers import init, get_last_feed, get_podcasts_config, write_feeds_file, get_version
from common.psapi import get_podcast_metadata, get_episode_manifest, get_podcast_episodes, get_all_podcast_episodes, get_all_podcast_episodes_all_seasons

podgen_agent = f"nrk-pod-feeder v{get_version()} (with help from python-podgen)"
podcasts_cfg_file = "podcasts.json"
filter_teasers = True
web_url = "https://jensbech.github.io/nrk-pod-feeds"

def get_podcast(podcast_id, season, feeds_dir, ep_count = 10):
    existing_feed = get_last_feed(feeds_dir, podcast_id)

    last_feed_update = parser.parse("1970-01-01 00:00:01+00:00")
    if existing_feed:
        for channel in existing_feed.findall('channel'):
            last_build_date = channel.find('lastBuildDate').text
            last_feed_update = parser.parse(last_build_date)
            logging.debug(f"Feed was last built {last_feed_update}")

    metadata = get_podcast_metadata(podcast_id)
    if not metadata:
        return None

    original_title = metadata["series"]["titles"]["title"]
    title_match = re.match(r'^De \d+ siste fra (.+)$', original_title)
    if title_match:
        original_title = title_match.group(1)
    sq = metadata['series'].get('squareImage') or []
    image = f"{sq[-1]['url']}.jpg" if sq else ""
    website = metadata["_links"]["share"]["href"]

    logging.debug(f"  Title: {original_title}")
    logging.debug(f"  Image: {image}")

    p = Podcast(
        generator=podgen_agent,
        website=web_url,
        image=image,
        withhold_from_itunes=True,
        explicit=False,
        language="no"
    )

    if season == "LATEST_SEASON":
        season = metadata["_links"]["seasons"][0]["name"]

    latest = get_podcast_episodes(podcast_id, season, page_size=5)
    if not latest:
        return None

    two_years_ago = datetime.now(timezone.utc) - timedelta(days=730)
    if parser.parse(latest[0]["date"]) < two_years_ago:
        logging.info("  Last episode is over 2 years old, skipping")
        return None

    if existing_feed:
        if not any(parser.parse(e["date"]) >= last_feed_update for e in latest):
            logging.info("  No new episodes found since feed was last updated")
            return None

    if ep_count == 0:
        if season == "ALL":
            episodes = get_all_podcast_episodes_all_seasons(podcast_id, metadata)
        else:
            episodes = get_all_podcast_episodes(podcast_id, season)
    else:
        episodes = get_podcast_episodes(podcast_id, season, page_size=ep_count)

    if not episodes:
        return None

    ep_i = 0
    for episode in episodes:
        logging.info(f"Episode #{ep_i}:")

        episode_id = episode["episodeId"]
        episode_title = episode["titles"]["title"]
        episode_subtitle = episode["titles"]["subtitle"]
        sq = episode.get('squareImage') or []
        episode_image = f"{sq[-1]['url']}.jpg" if sq else ""
        duration = episode["durationInSeconds"]
        date = episode["date"]
        
        manifest = get_episode_manifest(podcast_id, episode_id)
        if not manifest:
            continue

        audio_mime = manifest["playable"]["assets"][0]["mimeType"]
        audio_url = manifest["playable"]["assets"][0]["url"]

        logging.info(f"  Episode title: {episode_title}")
        logging.info(f"  Episode duration: {duration}")
        logging.info(f"  Episode date: {date}")
        logging.info(f"  Audio file URL: {audio_url}")
        logging.info(f"  Episode image URL: {episode_image}")

        if audio_mime != "audio/mp3":
            logging.info(f"  Unrecognized audio MIME type ({audio_mime})")
            continue

        if filter_teasers and episode_title.startswith("Neste episode: "):
            logging.info("  Skipping teaser")
            continue

        p.episodes += [
            Episode(
                title=episode_title,
                media=Media(audio_url, 0, duration=timedelta(seconds=duration)),
                summary=episode_subtitle,
                publication_date=parser.parse(date),
                image=episode_image
            ),
        ]

        ep_i +=1

    title = original_title
    subtitle = metadata["series"]["titles"].get("subtitle", "")

    p.name = title
    p.description = subtitle

    return p

def write_podcast_xml(feeds_dir, podcast_id, podcast):
    output_path = f"{feeds_dir}/{podcast_id}.xml"
    podcast.rss_file(output_path, minimize=False)

    logging.info(f"Podcast XML successfully written to file: {output_path}\n---")
    return output_path

if __name__ == '__main__':
    init()

    feeds_dir = "docs/rss"
    feeds_file = "docs/feeds.js"

    podcasts = get_podcasts_config(podcasts_cfg_file)

    inactive_refresh_days = random.randint(50, 60)

    for p in podcasts:
        podcast_id = p["id"]
        podcast_season = p["season"]
        ep_count = 100 if p["enabled"] else 50

        if "episodes" in p:
            ep_count = p["episodes"]

        ep_count = min(ep_count, 100) if ep_count > 0 else 100

        if not p["enabled"]:
            existing = get_last_feed(feeds_dir, podcast_id)
            if existing:
                for channel in existing.findall('channel'):
                    last_built = parser.parse(channel.find('lastBuildDate').text)
                    days_since = (datetime.now(timezone.utc) - last_built).days
                    if days_since < inactive_refresh_days:
                        logging.debug(f"Skipping inactive podcast {podcast_id} (built {days_since}d ago)")
                        ep_count = -1
            if ep_count == -1:
                continue

        podcast = get_podcast(podcast_id, podcast_season, feeds_dir, ep_count)
        if not podcast:
            logging.debug(f"Got empty result when fetching podcast {podcast_id}")
            continue

        write_podcast_xml(feeds_dir, podcast_id, podcast)

    write_feeds_file(feeds_file, podcasts)
    logging.info("Done")
