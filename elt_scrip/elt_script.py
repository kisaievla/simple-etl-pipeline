import subprocess  # Allows running shell commands from Python
import time  # Used for adding delays during retries

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available before proceeding."""
    retries = 0
    while retries < max_retries:
        try:
            # Runs the 'pg_isready' command to check if PostgreSQL is accepting connections
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True
            )
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True  # Database is ready, exit loop
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)  # Wait before retrying

    print("Max retries reached. Exiting.")
    return False  # Database did not become available

# Use the function before running the ELT process
if not wait_for_postgres(host="source_postgres"):
    exit(1)  # If the source database is not available, exit the script

print("Starting ELT script...")

# Configuration for the source PostgreSQL database
source_config = {
    'dbname': 'source_db',  # Database name
    'user': 'postgres',  # Username
    'password': 'secret',  # Password
    'host': 'source_postgres'  # Hostname (from docker-compose)
}

# Configuration for the destination PostgreSQL database
destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'destination_postgres'
}

# Step 1: Dump the source database using `pg_dump`
dump_command = [
    'pg_dump',
    '-h', source_config['host'],  # Host of source DB
    '-U', source_config['user'],  # Username
    '-d', source_config['dbname'],  # Database name
    '-f', 'data_dump.sql',  # Output file
    '-w'  # Do not prompt for password (uses PGPASSWORD)
]

# Set the PGPASSWORD environment variable to avoid password prompt
subprocess_env = dict(PGPASSWORD=source_config['password'])

# Execute the dump command
subprocess.run(dump_command, env=subprocess_env, check=True)

# Step 2: Load the dumped SQL file into the destination database using `psql`
load_command = [
    'psql',
    '-h', destination_config['host'],  # Host of destination DB
    '-U', destination_config['user'],  # Username
    '-d', destination_config['dbname'],  # Database name
    '-a', '-f', 'data_dump.sql'  # Execute SQL file
]

# Set the PGPASSWORD environment variable for the destination database
subprocess_env = dict(PGPASSWORD=destination_config['password'])

# Execute the load command
subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ELT script...")
