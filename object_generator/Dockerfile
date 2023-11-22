# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies for OpenGL
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    xvfb \
    libosmesa6 \
    libglfw3 \
    x11-apps \
    libxext-dev \
    libxrender-dev \
    libxtst-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Define environment variable
ENV NAME World

# Run app.py when the container launches
# CMD ["python", "test_render.py"]
# CMD ["xvfb-run", "-e", "/dev/stdout", "--server-num=1", "--server-args=-screen 0 1024x768x24", "python", "test_render.py"]

# run indefinitely
CMD tail -f /dev/null

