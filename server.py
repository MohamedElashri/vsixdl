from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

MARKETPLACE_API = 'https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery'

async def check_platform_support(session, publisher, extension, version, platform):
    # First try with the full platform string
    url = f'https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension}/{version}/vspackage'
    if platform != 'universal':
        url += f'?targetPlatform={platform}'
    
    print(f"Checking URL: {url}")  # Debug log
    try:
        async with session.get(url, allow_redirects=True) as response:
            print(f"Response for {platform}: {response.status}")  # Debug log
            # If it's not found and this is an x86_64 architecture, try without architecture
            if response.status == 404 and platform.endswith('x86_64'):
                os_name = platform.split('-')[0]
                base_url = f'https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension}/{version}/vspackage?targetPlatform={os_name}'
                async with session.get(base_url, allow_redirects=True) as base_response:
                    print(f"Response for {os_name}: {base_response.status}")  # Debug log
                    return platform, base_response.status in [200, 302]
            return platform, response.status in [200, 302]  # Include 302 (redirect) as success
    except Exception as e:
        print(f"Error checking {platform}: {str(e)}")  # Debug log
        return platform, False

async def get_supported_platforms(publisher, extension, version):
    platforms = {
        'win32': ['x86_64', 'arm64', 'ia32'],
        'linux': ['x86_64', 'arm64', 'armhf'],
        'darwin': ['x86_64', 'arm64'],
        'web': ['web']
    }
    
    # First check all platforms to see what's available
    supported = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Check platform-specific URLs first
        for os_name, architectures in platforms.items():
            for arch in architectures:
                platform = f"{os_name}-{arch}"
                if os_name == 'web':
                    platform = 'web'
                tasks.append(check_platform_support(session, publisher, extension, version, platform))
        
        results = await asyncio.gather(*tasks)
        
        # Process platform-specific results
        has_platform_specific = False
        for platform, is_supported in results:
            if is_supported:
                has_platform_specific = True
                os_name = platform.split('-')[0] if '-' in platform else platform
                arch = platform.split('-')[1] if '-' in platform else 'web'
                if os_name not in supported:
                    supported[os_name] = []
                if arch not in supported[os_name]:
                    supported[os_name].append(arch)
        
        # Only check for universal if no platform-specific versions were found
        if not has_platform_specific:
            url = f'https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension}/{version}/vspackage'
            try:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status in [200, 302]:
                        print(f"Extension {publisher}.{extension} v{version} is universal")
                        return {'universal': True}
            except Exception as e:
                print(f"Error checking universal: {str(e)}")
    
    print(f"Supported platforms for {publisher}.{extension} v{version}: {supported}")
    return supported

@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/versions', methods=['POST'])
def get_versions():
    try:
        request_data = request.json
        # Get the max_versions parameter from the request, default to 5
        max_versions = request_data.get('max_versions', 5)
        
        response = requests.post(
            MARKETPLACE_API,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json;api-version=7.1-preview.1',
                'User-Agent': 'Mozilla/5.0'
            },
            json=request_data
        )
        response.raise_for_status()
        data = response.json()
        
        if not data['results'] or not data['results'][0]['extensions']:
            return jsonify({'error': 'Extension not found'}), 404
            
        extension_data = data['results'][0]['extensions'][0]
        publisher = extension_data['publisher']['publisherName']  
        extension_id = extension_data['extensionName']  
        
        print(f"Checking platforms for {publisher}.{extension_id}")  

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Limit versions if max_versions is not -1 (all versions)
        versions_to_process = extension_data['versions']
        if max_versions != -1:
            versions_to_process = versions_to_process[:max_versions]
            
        for version in versions_to_process:
            supported_platforms = loop.run_until_complete(
                get_supported_platforms(publisher, extension_id, version['version'])
            )
            version['supportedPlatforms'] = supported_platforms
            print(f"Version {version['version']} supported platforms: {supported_platforms}")  

        loop.close()
        
        # Add total version count to response
        data['results'][0]['extensions'][0]['totalVersionCount'] = len(extension_data['versions'])
        data['results'][0]['extensions'][0]['versions'] = versions_to_process
        
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
