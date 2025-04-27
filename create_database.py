import duckdb
import pandas as pd
import requests
from io import StringIO


def get_github_file_urls(user, repo, folder_path, branch='main'):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{folder_path}?ref={branch}"
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch content: {response.status_code}, {response.text}")
    items = response.json()
    file_urls = [item['download_url'] for item in items if item['type'] == 'file']
    return file_urls


def upload_files_to_duckdb(csv_urls, con):
    for url in csv_urls:
        try:
            # Download the CSV file
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            # Read the CSV content into a Pandas DataFrame
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            # Extract table name from the URL (e.g., file1.csv -> file1)
            table_name = url.split("/")[-1].split(".")[0]
            # Upload the DataFrame to DuckDB
            con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
            print(f"Uploaded data to table: {table_name}")
        except Exception as e:
            print(f"Failed to process {url}: {e}")


def main():
    user = 'oleg-agapov'
    repo = 'the_ruum_dataset'
    folder_path = 'output'
    branch = 'main'

    urls = get_github_file_urls(user, repo, folder_path, branch)
    # DuckDB database file
    duckdb_file = "dev.duckdb"
    # Connect to DuckDB
    con = duckdb.connect(duckdb_file)
    upload_files_to_duckdb(urls, con)
    # Close the DuckDB connection
    con.close()

if __name__ == '__main__':
    main()
