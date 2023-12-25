################################################################################
"""
Split a Multi-Channel WAV file into Individual Mono files.

Reference:
https://video.stackexchange.com/questions/22024/extract-all-audio-channels-as-separate-wave-file-from-a-multichannel-file

(c) 2023 - Stanley Solutions | Joe Stanley
"""
################################################################################

import json
import argparse
from pathlib import Path

from ffmpeg import FFmpeg

def determine_number_channels(path: str | Path):
    """Use ffprobe to Gather the Number of Channels in File."""
    ffprobe = FFmpeg(
        executable="ffprobe"
    ).input(
        path,
        v="error",
        show_entries="stream=channels,channel_layout",
        of="default=nw=1",
        print_format="json",
    )
    media = json.loads(ffprobe.execute())
    return media["streams"][0]["channels"]

def perform_split(path: str | Path, n_channels: int, output_path: str):
    """Use ffmpeg to Perform the Split."""
    channel_split_arg = ''
    for i in range(n_channels):
        if i > 0:
            channel_split_arg += ";"
        channel_split_arg += f"[0:a]pan=mono|c0=c{i}[a{i}]"
    ffmpeg = FFmpeg().input(
        path,
        filter_complex=channel_split_arg,
    )
    for i in range(n_channels):
        ffmpeg = ffmpeg.output(f"{output_path}chan_{i}.wav", map=f'[a{i}]')

    _ = ffmpeg.execute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='QuickTrackSplit',
        description='Split a Multi-Channel WAV File into Individual Mono Files',
        epilog='(c) 2023 - Stanley Solutions | Joe Stanley'
    )
    parser.add_argument(
        'filename', help="path to the WAV file to split"
    )
    parser.add_argument(
        '-o', '--output', help="path to store the output files", default="./"
    )
    args = parser.parse_args()

    num_channels = determine_number_channels(args.filename)
    print(f"Detected {num_channels} channels. Splitting individual files...")
    perform_split(args.filename, num_channels, args.output)
