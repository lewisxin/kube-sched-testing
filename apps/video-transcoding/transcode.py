import ffmpeg
import argparse
import os

supported_resolutions = ["640x360", "1280x720", "1920x1080"]
bandwith = {
    '640x360': 500000,
    '1280x720': 1000000,
    '1920x1080': 2000000
}

def generate_master_playlist(output_directory, resolutions):
    master_playlist_path = os.path.join(output_directory, 'master_playlist.m3u8')
    os.makedirs(output_directory, exist_ok=True)

    with open(master_playlist_path, 'w') as master_playlist:
        master_playlist.write("#EXTM3U\n")
        master_playlist.write("#EXT-X-VERSION:3\n")

        for resolution in resolutions:
            _, height = map(int, resolution.split('x'))
            playlist_file = f'{resolution}/{height}p.m3u8'
            master_playlist.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwith[resolution]},RESOLUTION={resolution}\n")
            master_playlist.write(f"{playlist_file}\n")

def transcode_segment(input_file, output_directory, total_duration, resolution):
    width, height = map(int, resolution.split('x'))
    output_directory = os.path.join(output_directory, f'{width}x{height}')
    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, f'{height}p.m3u8')
    hls_segment_filename = os.path.join(output_directory, f'{height}p_%03d.ts')

    ffmpeg.input(input_file).output(
        output_file_path,
        vcodec='libx264',
        acodec='copy',
        t=total_duration,
        vf=f'scale={width}:{height}',
        hls_time=20,
        hls_segment_filename=hls_segment_filename,
        hls_playlist_type='event',
        strict='experimental'
    ).run()

def get_total_duration(input_file):
    probe = ffmpeg.probe(input_file)
    return float(probe['format']['duration'])

def main():
    parser = argparse.ArgumentParser(description='Transcode video segments based on the output file type')
    parser.add_argument('input_file', help='Input video file (e.g., input.mp4)')
    parser.add_argument('output_directory', help='Output directory for HLS files')
    parser.add_argument('resolution_index', help='Index of resolution of the output HLS streams (0=640x360, 1=1280x720, 2=1920x1080)')
    args = parser.parse_args()

    total_duration = get_total_duration(args.input_file)

    transcode_segment(args.input_file, args.output_directory, total_duration, supported_resolutions[int(args.resolution_index)])
    generate_master_playlist(args.output_directory, supported_resolutions)

if __name__ == "__main__":
    main()
