import re
import requests
import time

def fetch_and_convert_playlist():

    playlist_url = "https://sayan-jiotv.spal75084.workers.dev/playlist.m3u"
    
    print("Fetching playlist from:", playlist_url)
    
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    try:
        # Fetch the playlist
        response = requests.get(playlist_url, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.text
        
        print(f"✓ Fetched {len(content)} characters")
        
        # Process the content
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        # Add M3U header if missing
        if not content.startswith('#EXTM3U'):
            new_lines.append('#EXTM3U')
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXTINF:'):
                # Store EXTINF line
                extinf_line = line
                i += 1
                
                # Collect KODIPROP lines
                property_lines = []
                while i < len(lines) and lines[i].strip().startswith('#KODIPROP'):
                    property_lines.append(lines[i].strip())
                    i += 1
                
                # Collect EXTVLCOPT lines
                vlcopt_lines = []
                while i < len(lines) and lines[i].strip().startswith('#EXTVLCOPT'):
                    vlcopt_lines.append(lines[i].strip())
                    i += 1
                
                # Get the URL
                if i < len(lines):
                    url = lines[i].strip()
                    i += 1
                    
                    # Extract __hdnea__ for cookie
                    hdnea_match = re.search(r'__hdnea__=([^&\s]+)', url)
                    if hdnea_match:
                        cookie_value = f"__hdnea__={hdnea_match.group(1)}"
                        exthttp_line = f'#EXTHTTP:{{"cookie":"{cookie_value}","Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}'
                        
                        # Add all lines in correct order
                        new_lines.append(extinf_line)
                        new_lines.extend(property_lines)
                        new_lines.extend(vlcopt_lines)
                        new_lines.append(exthttp_line)
                        new_lines.append(url)
                        new_lines.append('')
                    else:
                        # No __hdnea__ found
                        new_lines.append(extinf_line)
                        new_lines.extend(property_lines)
                        new_lines.extend(vlcopt_lines)
                        new_lines.append(url)
                        new_lines.append('')
                        
            elif line.startswith('http'):
                # Handle standalone URLs
                hdnea_match = re.search(r'__hdnea__=([^&\s]+)', line)
                if hdnea_match:
                    cookie_value = f"__hdnea__={hdnea_match.group(1)}"
                    exthttp_line = f'#EXTHTTP:{{"cookie":"{cookie_value}","Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}'
                    new_lines.append(exthttp_line)
                new_lines.append(line)
                new_lines.append('')
                
            elif line and not line.startswith('#'):
                # Skip any other non-comment lines that aren't URLs
                pass
                
            else:
                # Keep other comment lines
                if line:
                    new_lines.append(line)
            
            i += 1
        
        
        result = '\n'.join(new_lines)
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        
        output_file = "jtvplus7.m3u"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"✓ Successfully saved as: {output_file}")
        print(f"✓ Stream entries found: {result.count('#EXTINF:')}")
        
        
        preview = result.split('\n')[:10]
        print("\nPreview:")
        print("-" * 50)
        for p in preview:
            if p:
                print(p[:80] + "..." if len(p) > 80 else p)
        print("-" * 50)
        
        return True
        
    except requests.exceptions.Timeout:
        print("✗ Timeout - The server is taking too long to respond")
        print("  Tip: Try again later or check if the URL is still valid")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error - Cannot reach the server")
        print("  Tip: Check your internet connection or try using a VPN")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error {e.response.status_code}")
        if e.response.status_code == 404:
            print("  The playlist URL no longer exists")
        elif e.response.status_code == 403:
            print("  Access denied - You might need to use a different URL")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("JioTV Playlist Converter - Direct Mode")
    print("=" * 50)
    success = fetch_and_convert_playlist()
    if success:
        print("\n✓ Done! Check jtvplus7.m3u")
    else:
        print("\n✗ Conversion failed")
