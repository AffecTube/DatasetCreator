import os.path

from pytube import YouTube


def video_download(video_name, out_dir):
    """
    Downloads video with given name from YouTube
    :param video_name: Video name (code)
    :param out_dir: Output directory
    """
    file_name = f"{video_name}.mp4"
    if not os.path.exists(f"{out_dir}/{file_name}"):
        print(f"Downloading https://youtu.be/{video_name} ...")
        yt = YouTube(f"https://youtu.be/{video_name}")
        yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(filename=f"{out_dir}/{file_name}")
        print(f"Video downloaded: {out_dir}/{file_name}")
    else:
        print(f"File {video_name} is already downloaded...")
