import os.path

from yt_dlp import YoutubeDL


def video_download(video_name, out_dir):
    """
    Downloads video with given name from YouTube
    :param video_name: Video name (code)
    :param out_dir: Output directory
    """
    file_name = f"{video_name}.mp4"
    if not os.path.exists(f"{out_dir}/{file_name}"):
        print(f"Downloading https://youtu.be/{video_name} ...")
        ydl_opts = {
            # best mp4 video + m4a audio merged into mp4, fall back to best single mp4 file
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]',
            'merge_output_format': 'mp4',
            'outtmpl': f"{out_dir}/{file_name}",
            'quiet': True,
            'no_warnings': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://youtu.be/{video_name}"])
        print(f"Video downloaded: {out_dir}/{file_name}")
    else:
        print(f"File {video_name} is already downloaded...")
