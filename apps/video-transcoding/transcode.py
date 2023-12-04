import ffmpeg
import argparse
import os

def transcode_segment(input_file, output_file, segment, segment_duration, total_duration):
    # Calculate start time and end time for the segment
    start_time = segment * segment_duration
    end_time = min((segment + 1) * segment_duration, total_duration)

    # Extract the file extension from the output_file argument
    output_file_extension = os.path.splitext(output_file)[1][1:]  # Remove the leading dot

    # Construct the ffmpeg command for the specific segment
    (
        ffmpeg.input(input_file, ss=start_time)
        .output(f'output_{segment}.{output_file_extension}', vcodec='libx264', acodec='aac', t=end_time - start_time, strict='experimental')
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
    parser.add_argument('num_segments', type=int, help='Number of segments')
    args = parser.parse_args()

    total_duration = get_total_duration(args.input_file)  # Calculate the total duration of the input video

    # Transcode each segment
    for segment in range(args.num_segments):
        transcode_segment(args.input_file, args.output_file, segment, total_duration / args.num_segments, total_duration)

if __name__ == "__main__":
    main()
