import ffmpeg
import os
import argparse

def combine_segments(output_segments_dir, output_file):
    # List all output segment files in the directory and sort them
    input_files = sorted([os.path.join(output_segments_dir, file) for file in os.listdir(output_segments_dir) if file.startswith('output_')])

    # Generate an absolute path for the temporary text file
    temp_list_file = os.path.abspath('input_files.txt')

    with open(temp_list_file, 'w') as file:
        file.writelines([f"file '{input_file}'\n" for input_file in input_files])

    # Use ffmpeg to concatenate the input files into the output file
    (
        ffmpeg.input(temp_list_file, format='concat', safe=0)
        .output(output_file, c='copy', movflags='faststart', f='mov')
        .run()
    )

    # Remove the temporary list file
    os.remove(temp_list_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Combine video segments into a single MOV file')
    parser.add_argument('output_segments_dir', help='Directory containing output video segments')
    parser.add_argument('output_file', help='Output video file name (MOV format)')
    args = parser.parse_args()

    # Combine all segments into a single MOV file
    combine_segments(args.output_segments_dir, args.output_file)

    print(f"Combined segments into {args.output_file}")
