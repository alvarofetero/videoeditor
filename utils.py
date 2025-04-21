import subprocess
import os
import tempfile

def export_clips(video_path, tags, output_dir, ffmpeg_cmd="ffmpeg"):
    if len(tags) < 2:
        return
    if len(tags) % 2 != 0:
        tags = tags[:-1]

    for i in range(0, len(tags), 2):
        start = tags[i]
        end = tags[i+1]
        output_file = os.path.join(output_dir, f"clip_{i//2 + 1}.mp4")
        cmd = [
            ffmpeg_cmd,
            "-i", video_path,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            output_file
        ]
        subprocess.run(cmd)



def generate_proxy(video_path, resolution="640x360"):
    proxy_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    output_path = proxy_file.name

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"scale={resolution}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "35",
        "-c:a", "aac",
        "-y",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

