import os
import sys
import time
import glob
import urllib.error
from pathlib import Path

import pytube.exceptions
from pytube import YouTube


# VERSION of this application
VERSION = "0.2.2"
# DOWNLOADS_DIR defines to the parent downloads directory
DOWNLOADS_DIR = "./downloads/"
# LINK_FILE_GLOB defines the glob used to find link files
LINK_FILE_GLOB = "videos-*.txt"


def pytube_on_progress(stream, chunk, file_handle, bytes_remaining):
    """PyTube On Progress Callback Function

    Function called by PyTube everytime a chunk is received. Calculates
    downloaded percentage, rounds to the nearest whole number and 
    prints to the terminal.
    """
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining 
    percentage_of_completion = bytes_downloaded / total_size * 100
    carriage_return()
    print(f"({link_current}/{links_count}) Downloading:", 
        f"{round(percentage_of_completion)}%", end="", flush=True)


def pytube_on_complete(stream, file_handle):
    """PyTube On Complete Callback Function

    Function called by PyTube once download is received. Prints to 
    terminal.
    """
    carriage_return()
    print(f"({link_current}/{links_count}) Complete: {file_handle.name}")


def negative_glob_match(glob, string):
    """Negative Glob Match Helper Function

    Returns the matching wildcard ("*") value of a glob. For example
    given the glob "*-airspeed.txt" and the filename (string)
    "swallow-airspeed.txt" will return "swallow". 

    Arguments
    ---------
    glob : string
        A glob.
    string : string
        A string the glob matched.

    Returns
    -------
    string
        The wildcard ("*") portion of the string the glob matched.

    """
    match = string
    for s in glob.split("*"):
        match = match.replace(s, "")
    return match


def carriage_return():
    """Carriage Return Helper Function

    Prints an arbitrary number of blank spaces followed by a carriage
    return to clear the terminal line. 
    """
    print(70*" ", end="\r")


def increment_count():
    """Increment Count Helper Function

    Increments the count of link_current. This only seemed to work once
    broken out into a separate function. 
    """
    global link_current
    link_current += 1


def download_from_link(link, file_name, max_retries=3):
    """Download YouTube Video From Link

    Attempts to download the highest quality mp4 progressive video stream
    available for the given YouTube video link. Handles failures 
    gracefully and will attempt retries. Checks whether or not the file
    has already been downloaded and skips if so.

    Arguments
    ---------
    link : string
        YouTube video link.
    file_name : string
        The name of the link list file used to determine download sub directory.
    max_retries : int
        Maximum amount of retry attempts before moving on. Defaults to "3".

    Returns
    -------
    bool
        Returns False on download failure and True on success.

    """
    retry_attempt = 1
    retry_delay = 0
    while (retry_attempt < max_retries):
        time.sleep(retry_delay)
        print(f"Trying: {link}... ", end="", flush=True)
        # attempt to load video from link
        try:
            yt = YouTube(link)
        except pytube.exceptions.VideoUnavailable:
            carriage_return()
            print(f"Failed: Video {link} is unavailable. Retrying...", 
                f"(Attempt {retry_attempt}/{max_retries})")
            retry_delay += 2
            continue
        except KeyError as key:
            carriage_return()
            print(f"Failed: KeyError on {key} for video {link}.", 
                f"Retrying... (Attempt {retry_attempt}/{max_retries})")
            retry_delay += 2
            continue
        # check if target download directory exists
        target_path = Path(
            DOWNLOADS_DIR, negative_glob_match(LINK_FILE_GLOB, file_name))
        if target_path.exists() and target_path.is_dir():
            pass
        elif target_path.exists() and not target_path.is_dir():
            pass
        elif not target_path.exists():
            os.makedirs(target_path) # try?
        else:
            pass
        # check if filename already exists in target directory
        yt.register_on_progress_callback(pytube_on_progress)
        yt.register_on_complete_callback(pytube_on_complete)
        stream = yt.streams.filter(subtype='mp4', progressive=True).first()
        target_file = Path(target_path, stream.default_filename)
        if target_file.exists() and not target_file.is_dir():
            carriage_return()
            print(f"({link_current}/{links_count}) Skipping:", 
                f"{stream.default_filename} ({link})")
            break
        try:
            stream.download(target_path)
        except urllib.error.HTTPError as err:
            print(f"\nFailed: HTTP Error {err.code}: {err.reason}.", 
                f"Retrying... (Attempt {retry_attempt}/{max_retries})")
            sleep_time += 2
            continue
        break
    if retry_attempt > max_retries:
        return False
    else:
        return True


def main():
    """Main Function

    Checks for link list file(s), itterates over them and attempts to
    download videos.
    """
    # check for link files
    if len(glob.glob(LINK_FILE_GLOB)) == 0:
        sys.exit("No link files found :(")
    # load each file matching the defined glob and count the links
    for file_name in glob.glob(LINK_FILE_GLOB):
        global links_count
        links_count = 0
        print(f"Loading '{file_name}'")
        # count links in file
        with open(file_name) as f:
            for i in enumerate(f):
                links_count += 1
        # start downloading links from file
        with open(file_name) as links:
            global link_current
            link_current = 1
            for link in links:
                link = link.rstrip(os.linesep)
                if link.strip() == "":
                    continue
                if download_from_link(link, file_name):
                    increment_count()
                else:
                    print(f"Failed to download {link}.")
        print(f"Finished '{file_name}'")


main()