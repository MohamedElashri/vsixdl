import re
import argparse
import logging
from colorama import Fore, Style

try:
    import requests
    requests_available = True
except ImportError:
    requests_available = False

# Setup logging
class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = {
            logging.ERROR: Fore.RED,
            logging.WARNING: Fore.YELLOW,
            logging.INFO: Fore.CYAN,
            logging.DEBUG: Fore.GREEN,
        }.get(record.levelno, Fore.WHITE)
        return f"{color}{record.msg}{Style.RESET_ALL}"

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logger = logging.getLogger("ExtensionDownloader")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_extension_versions(publisher, extension_name):
    """Fetch all available versions of the extension using the VSCode Marketplace API."""
    api_url = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;api-version=6.1-preview.1"
    }
    payload = {
        "filters": [{
            "criteria": [
                {"filterType": 7, "value": f"{publisher}.{extension_name}"}
            ]
        }],
        "flags": 914
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            versions = data['results'][0]['extensions'][0]['versions']
            return [version['version'] for version in versions]
        else:
            logger.error(f"Unable to fetch metadata. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def parse_input(input_string):
    """Parse user input to extract publisher and extension name."""
    match_full_url = re.search(r"itemName=([^.]+)\.(.+)", input_string)
    match_id = re.match(r"([^.]+)\.(.+)", input_string)

    if match_full_url:
        return match_full_url.groups()
    elif match_id:
        return match_id.groups()
    else:
        return None, None

def download_extension(publisher, extension_name, version):
    """Download the specified version of the extension."""
    download_url = (
        f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/"
        f"{extension_name}/{version}/vspackage"
    )
    logger.info(f"Downloading version {version} of {publisher}.{extension_name}...")
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            file_name = f"{extension_name}-{version}.vsix"
            with open(file_name, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.info(f"File downloaded successfully as '{file_name}'")
        else:
            logger.error(f"Failed to download the file. HTTP Status Code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error during download: {e}")

def main():
    parser = argparse.ArgumentParser(description="VSCode Extension Downloader")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List subcommand
    list_parser = subparsers.add_parser("list", help="List available versions of an extension")
    list_parser.add_argument(
        "--id", 
        required=True, 
        help="Extension ID or URL (e.g., ms-toolsai.jupyter or full Marketplace URL)"
    )

    # Download subcommand
    download_parser = subparsers.add_parser("download", help="Download a specific or latest version of an extension")
    download_parser.add_argument(
        "--id", 
        required=True, 
        help="Extension ID or URL (e.g., ms-toolsai.jupyter or full Marketplace URL)"
    )
    download_parser.add_argument(
        "--version", 
        help="Specific version to download (omit to download the latest version)"
    )

    # Parse arguments
    args = parser.parse_args()

    # Parse ID to extract publisher and extension name
    publisher, extension_name = parse_input(args.id)
    if not publisher or not extension_name:
        logger.error("Invalid extension ID or URL format. Use 'publisher.extension' or full URL.")
        return

    # Handle subcommands
    if args.command == "list":
        logger.info(f"Fetching available versions for {publisher}.{extension_name}...")
        versions = get_extension_versions(publisher, extension_name)
        if versions:
            logger.info("\nAvailable Versions:")
            for i, version in enumerate(versions, start=1):
                print(f"{i}. {version}")
        else:
            logger.error("Failed to fetch versions.")
    elif args.command == "download":
        if args.version:
            version = args.version
        else:
            logger.info(f"Fetching the latest version for {publisher}.{extension_name}...")
            versions = get_extension_versions(publisher, extension_name)
            if versions:
                version = versions[0]
                logger.info(f"Latest version: {version}")
            else:
                logger.error("Failed to fetch the latest version.")
                return
        download_extension(publisher, extension_name, version)

if __name__ == "__main__":
    main()