FROM python:3.8

# Copy the requirements.txt file to the working directory
WORKDIR fetch_dir

COPY . .

# Install the required Python packages
RUN pip install -r requirements.txt

# Run the Python script when the container launches, passing in any command line arguments and the metadata flag
CMD ["python", "main.py", "--metadata", "https://stackoverflow.com", "https://autify.com"]

