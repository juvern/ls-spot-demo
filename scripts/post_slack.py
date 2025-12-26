import json
import os
import time
import requests

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
COURSES_PATH = os.environ.get("COURSES_PATH", "courses.json")

API_BASE = "https://slack.com/api"

THREAD_TEMPLATE = (
    "If interested in attending a session, please provide your availability and let us know "
    "by commenting here so that a spot lead can take this session. If a lead isn't available "
    "by mid-week, it is advised that everyone pair up. Students must follow the LS code of conduct.\n\n"
    "{course}: {link}"
)

def slack_api(method: str, payload: dict) -> dict:
    r = requests.post(
        f"{API_BASE}/{method}",
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json=payload,
        timeout=15,
    )
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"{method} failed: {data}")
    return data

def load_courses(path: str):
    with open(path, "r", encoding="utf-8") as f:
        courses = json.load(f)
    for item in courses:
        if "course" not in item or "link" not in item:
            raise ValueError(f"Bad item (need 'course' and 'link'): {item}")
    return courses

def main():
    courses = load_courses(COURSES_PATH)

    for item in courses:
        course = item["course"]
        link = item["link"]

        parent = slack_api("chat.postMessage", {
            "channel": CHANNEL_ID,
            "text": f"Reminder: {course} Study Session: Sign Up Here!",
        })

        thread_ts = parent["ts"]  # keep as string

        slack_api("chat.postMessage", {
            "channel": CHANNEL_ID,
            "thread_ts": thread_ts,
            "text": THREAD_TEMPLATE.format(course=course, link=link),
        })

        print(f"Posted {course} thread_ts={thread_ts}")

        # Slack guidance: generally ~1 msg/sec per channel for posting
        time.sleep(1.1)

if __name__ == "__main__":
    main()