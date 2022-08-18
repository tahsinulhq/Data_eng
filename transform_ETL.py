from logging import raiseExceptions
import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "	31gpoxvzolgjjajhaqrwsoufiziu"
TOKEN = "BQALbubcYpiExXh8EIWkpFyk-sh1HIRrXdR8pPEfXc3Np3fRMiJO63voIHVkgh0jd2yv05VsZ7LvMl-Gpv5JjGzEe-0eofu7Ry2-T3xw0UOAF-jD6auTnODoXNsXMwgyFIJ1JRkjvvLCCy9V6cS7d7yaG4LvRG9AMN_vEUrzMkv6i07MoEiFQ5CbQJhuabNal8YPGgSD5owH"

def check_if_valid_data(df: pd.DataFrame) -> bool:
    #check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False

    #Primary key check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key Check is violated")


    #Check for Nulls
    if df.isnull().values.any():
        raise Exception("Null value found")


    #check that all timestamp are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
            raise Exception("At least one of the returned songs does not come from within the last 24 hours")

    return True

if __name__ == "__main__":
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=TOKEN)
    
    }
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers=headers)

    data = r.json()

    # print(data)

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    song_dict = {
        "song_name" : song_names,
        "artist_name" : artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
    
    #Validate
    if check_if_valid_data(song_df):
        print("Data is valid, proceed to load stage")
    
    # print(song_df)