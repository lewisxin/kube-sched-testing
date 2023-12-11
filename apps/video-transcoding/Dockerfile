FROM python:3.8-slim as base

FROM base as base-installer
RUN apt update

FROM base-installer as ffmpeg-installer
RUN apt install --no-install-recommends -y ffmpeg

FROM base as runtime
COPY --from=ffmpeg-installer /usr/bin/ffprobe /usr/bin/ffprobe
COPY --from=ffmpeg-installer /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=ffmpeg-installer /usr/lib/*-linux-gnu/* /usr/lib/

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run transcode.py when the container launches
CMD ["python", "transcode.py", "./data/input.mp4", "./transcoded/", "0"]