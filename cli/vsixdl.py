import re
import argparse
import logging
from colorama import Fore, Style
import requests
import asyncio
import aiohttp

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

# Platform definitions
PLATFORMS = {
    'win32': ['x86_64', 'arm64', 'ia32'],
    'linux': ['x86_64', 'arm64', 'armhf'],
    'darwin': ['x86_64', 'arm64'],
    'web': ['web']
}

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

async def check_platform_support(session, publisher, extension_name, version, platform):
    """Check if a specific platform is supported for the extension."""
    url = f'https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension_name}/{version}/vspackage'
    if platform != 'universal':
        url += f'?targetPlatform={platform}'
    
    try:
        async with session.get(url, allow_redirects=True) as response:
            # If it's not found and this is an x86_64 architecture, try without architecture
            if response.status == 404 and platform.endswith('x86_64'):
                os_name = platform.split('-')[0]
                base_url = f'{url}?targetPlatform={os_name}'
                async with session.get(base_url, allow_redirects=True) as base_response:
                    return platform, base_response.status in [200, 302]
            return platform, response.status in [200, 302]
    except Exception as e:
        logger.error(f"Error checking {platform}: {str(e)}")
        return platform, False

async def get_supported_platforms(publisher, extension_name, version):
    """Get all supported platforms for the extension."""
    supported = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Check platform-specific URLs first
        for os_name, architectures in PLATFORMS.items():
            for arch in architectures:
                platform = f"{os_name}-{arch}"
                if os_name == 'web':
                    platform = 'web'
                tasks.append(check_platform_support(session, publisher, extension_name, version, platform))
        
        results = await asyncio.gather(*tasks)
        
        # Process results
        has_platform_specific = False
        for platform, is_supported in results:
            if is_supported:
                has_platform_specific = True
                supported[platform] = True
        
        # If no platform-specific versions found, try universal
        if not has_platform_specific:
            _, is_universal = await check_platform_support(session, publisher, extension_name, version, 'universal')
            if is_universal:
                supported['universal'] = True
        
        return supported

def download_extension(publisher, extension_name, version, platform=None):
    """Download the specified version of the extension."""
    download_url = (
        f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/"
        f"{extension_name}/{version}/vspackage"
    )
    
    if platform and platform != 'universal':
        download_url += f"?targetPlatform={platform}"
    
    logger.info(f"Downloading version {version} of {publisher}.{extension_name} for platform {platform or 'universal'}...")
    
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            platform_suffix = f"-{platform}" if platform and platform != 'universal' else ""
            file_name = f"{extension_name}-{version}{platform_suffix}.vsix"
            with open(file_name, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.info(f"File downloaded successfully as '{file_name}'")
        else:
            logger.error(f"Failed to download the file. HTTP Status Code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error during download: {e}")

def get_platform_list():
    """Get a list of all valid platform combinations."""
    platforms = ['universal', 'web']
    for os_name, architectures in PLATFORMS.items():
        if os_name != 'web':
            platforms.extend([f"{os_name}-{arch}" for arch in architectures])
    return platforms

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
    download_parser.add_argument(
        "--platform",
        help="Target platform (e.g., win32-x86_64, linux-arm64, darwin-arm64, web, or universal)"
    )
    download_parser.add_argument(
        "--list-platforms",
        action="store_true",
        help="List supported platforms for the specified version"
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

        if args.list_platforms:
            logger.info(f"Fetching supported platforms for {publisher}.{extension_name} version {version}...")
            supported_platforms = asyncio.run(get_supported_platforms(publisher, extension_name, version))
            if supported_platforms:
                logger.info("\nSupported Platforms:")
                for platform in supported_platforms:
                    print(f"- {platform}")
            else:
                logger.error("No supported platforms found.")
                return

        platform = args.platform
        if platform:
            # Validate platform format
            if platform != 'universal' and platform != 'web':
                os_name = platform.split('-')[0]
                arch = platform.split('-')[1] if '-' in platform else None
                if os_name not in PLATFORMS or (arch and arch not in PLATFORMS[os_name]):
                    logger.error(f"Invalid platform format. Use one of: {', '.join(get_platform_list())}")
                    return

        download_extension(publisher, extension_name, version, platform)

if __name__ == "__main__":
    main()