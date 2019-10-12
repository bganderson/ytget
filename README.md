# YTGet
Python YouTube Getter

Simple implementation of [pytube](https://github.com/nficano/pytube).

Downloads the highest quality progressive video stream from a list of YouTube links in a file. Born after 
coming up short trying to find a decent free macOS utility to download YouTube videos in bulk.

## Requirements
* Python 3.7+
* [pytube](https://github.com/nficano/pytube) 9.5.2+ ([HTTP 403 and KeyError Fix](https://github.com/nficano/pytube/pull/453))

## Usage

Assuming you meet the requirements listed above, create a file named `videos-SOME_NAME.txt` and fill it with 
YouTube links (one per line). Substitute `SOME_NAME` for whatever subdirectory name you want to be created in 
the `downloads` directory in your current working directory, which will contain your downloaded videos for 
that list. You can adjust the parent `downloads` directory and the naming format of the link list file 
(`videos-*.txt`) if desired by editing the constants near the top of `ytget.py`.

Run `ytget.py`

```python
python ytget.py
```
