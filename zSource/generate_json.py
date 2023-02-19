from github import Github
import json
import argparse
import pandas as pd
from utils import get_single_bundle_id, get_first_digit_index


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="Github token")
    args = parser.parse_args()
    token = args.token

    with open("apps.json", "r") as f:
        data = json.load(f)

    df = pd.read_csv("bundleId.csv")

    # clear apps
    data["apps"] = []

    g = Github(token)
    repo = g.get_repo("purp0s3/Tweaked-iOS-Apps")
    releases = repo.get_releases()

    for release in releases:
        print(release.title)

        for asset in release.get_assets():
            if (asset.name[-4:] != ".ipa"):
                continue
            name = asset.name[:-4]
            date = asset.created_at.strftime("%Y-%m-%d")
            try:
                app_name, tweaks = name.split("_", 1)
                idx = get_first_digit_index(app_name)
                app_name, version = app_name[:idx], app_name[idx:]
            except:
                app_name = name
                tweaks = ""
                version = "1.0"

            if tweaks.endswith("TS"):
                tweaks = "For TrollStore, injected with " + tweaks[:-2]

            if app_name in df.name.values:
                bundle_id = str(df[df.name == app_name].bundleId.values[0])
            else:
                bundle_id = get_single_bundle_id(asset.browser_download_url)
                df = pd.concat([df, pd.DataFrame(
                    {"name": [app_name], "bundleId": [bundle_id]})], ignore_index=True)

            data["apps"].append(
                {
                    "name": app_name,
                    "bundleIdentifier": bundle_id,
                    "version": version,
                    "versionDate": date,
                    "size": asset.size,
                    "downloadURL": asset.browser_download_url,
                    "developerName": "",
                    "localizedDescription": tweaks,
                    "iconURL": f"https://raw.githubusercontent.com/purp0s3/Tweaked-iOS-Apps/main/zSource/icons/{bundle_id}.png"
                }
            )

    df.to_csv("bundleId.csv", index=False)

    with open('apps.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
