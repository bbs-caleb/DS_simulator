import fire
import os
from urllib.parse import urlencode

import requests


BASE_URL = "https://cloud-api.yandex.net/v1/disk/public/resources/download?"


def download_yandex_disk(url: str, out: str) -> None:
    """Download data from Yandex Disk

    Args:
        url (str): Public data URL from Yandex Disk
        out (str): Output path to save downloaded data

    Raises:
        BaseException: Dataset cannot be downloaded
    """
    msg = f"File {out} already exists!"
    assert not os.path.exists(out), msg

    try:
        # Getting a full link
        full_url = BASE_URL + urlencode(dict(public_key=url))
        response = requests.get(full_url)
        download_url = response.json()["href"]

        # Save response to file
        download_response = requests.get(download_url)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as output_file:
            output_file.write(download_response.content)
    except Exception as e:
        raise BaseException("Dataset cannot be downloaded") from e


if __name__ == "__main__":
    fire.Fire(download_yandex_disk)
