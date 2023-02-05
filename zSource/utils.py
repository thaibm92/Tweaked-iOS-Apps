import requests
import zipfile
import plistlib
import github
import pandas as pd


def get_first_digit_index(string):
    for i, c in enumerate(string):
        if c.isdigit():
            return i
    return -1


def get_single_bundle_id(url, name="temp.ipa"):
    reponse = requests.get(url)
    open(name, 'wb').write(reponse.content)

    with zipfile.ZipFile(name, mode="r") as archive:
        for file_name in archive.namelist():
            if file_name.endswith(".app/Info.plist"):
                info_file = file_name

        with archive.open(info_file) as fp:
            pl = plistlib.load(fp)
            return pl["CFBundleIdentifier"]

    return "com.example.app"


def generate_bundle_id_csv(token=None):
    g = github.Github(token)
    repo = g.get_repo("purp0s3/Tweaked-iOS-Apps")
    releases = repo.get_releases()

    df = pd.DataFrame(columns=["name", "bundleId"])

    for release in releases:
        print(release.title)
        for asset in release.get_assets():
            if (asset.name[-4:] != ".ipa"):
                continue
            name = asset.name[:-4]

            try:
                app_name = name.split("_", 1)[0]
                app_name = app_name[:get_first_digit_index(app_name)]
            except:
                app_name = name

            if app_name in df.name.values:
                continue
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "name": [app_name],
                            "bundleId": get_single_bundle_id(asset.browser_download_url)
                        }
                    )
                ],
                ignore_index=True
            )

    df.to_csv("bundleId.csv", index=False)


if __name__ == "__main__":
    generate_bundle_id_csv()
