# Use the official Python 3.8 slim image as the base image (lighter version of Python)
FROM python:3.8-slim

# Update package lists and install PostgreSQL command-line tools (psql) to interact with the database
RUN apt-get update && apt-get install -y postgresql-client-15

# Copy the ELT script from the host machine into the container's working directory
COPY elt_script.py .

# Set the default command to execute the ELT script when the container starts
CMD ["python", "elt_script.py"]
