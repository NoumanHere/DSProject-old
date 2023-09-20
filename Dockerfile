# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install libgomp (adjust the package manager for your distribution)
RUN apt-get update && apt-get install -y libgomp1

# Make port 80 available to the world outside this container
EXPOSE 5000


# Run app.py when the container launches
#CMD ["python", "app.py"]
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]