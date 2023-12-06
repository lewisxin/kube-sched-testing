import ffmpeg
import argparse
import os

def transcode_segment(input_file, output_file, segment, segment_duration, total_duration):
    # Calculate start time and end time for the segment
    start_time = segment * segment_duration
    end_time = min((segment + 1) * segment_duration, total_duration)

    input_file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file_extension = os.path.splitext(output_file)[1][1:]  # Remove the leading dot
    output_directory = os.path.dirname(output_file)
    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, f'{input_file_name}_p{segment}.{output_file_extension}')

    # Construct the ffmpeg command for the specific segment
    (
        ffmpeg.input(input_file, ss=start_time)
        .output(output_file_path, vcodec='libx264', acodec='aac', t=end_time - start_time, strict='experimental')
        .run()
    )

def get_total_duration(input_file):
    # Use ffprobe to get the total duration of the input file
    probe = ffmpeg.probe(input_file)
    return float(probe['format']['duration'])

def main():
    parser = argparse.ArgumentParser(description='Transcode video segments based on the output file type')
    parser.add_argument('input_file', help='Input video file (e.g., input.mp4)')
    parser.add_argument('output_file', help='Output video file (e.g., output.mov or output.mp4)')
    parser.add_argument('num_segments', type=int, help='Total number of segments')
    parser.add_argument('segment', help='The segment to process')
    args = parser.parse_args()
    total_duration = get_total_duration(args.input_file)  # Calculate the total duration of the input video
    transcode_segment(args.input_file, args.output_file, int(args.segment), total_duration / args.num_segments, total_duration)

if __name__ == "__main__":
    main()
