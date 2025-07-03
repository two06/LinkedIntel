# LinkedIntel

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║    ██▓     ██▓ ███▄    █  ██ ▄█▀▓█████ ▓█████▄  ██▓ ███▄    █ ▄▄▄█████▓▓█████  ██▓   ║    
║   ▓██▒    ▓██▒ ██ ▀█   █  ██▄█▒ ▓█   ▀ ▒██▀ ██▌▓██▒ ██ ▀█   █ ▓  ██▒ ▓▒▓█   ▀ ▓██▒   ║    
║   ▒██▒    ▒██▒▓██  ▀█ ██▒▓███▄░ ▒███   ░██   █▌▒██▒▓██  ▀█ ██▒▒ ▓██░ ▒░▒███   ▒██▒   ║    
║   ░██░    ░██░▓██▒  ▐▌██▒▓██ █▄ ▒▓█  ▄ ░▓█▄   ▌░██░▓██▒  ▐▌██▒░ ▓██▓ ░ ▒▓█  ▄ ░██░   ║    
║   ░██░    ░██░▒██░   ▓██░▒██▒ █▄░▒████▒░▒████▓ ░██░▒██░   ▓██░  ▒██▒ ░ ░▒████▒░██░   ║    
║   ░▓      ░▓  ░ ▒░   ▒ ▒ ▒ ▒▒ ▓▒░░ ▒░ ░ ▒▒▓  ▒ ░▓  ░ ▒░   ▒ ▒   ▒ ░░   ░░ ▒░ ░░▓     ║    
║    ▒ ░     ▒ ░░ ░░   ░ ▒░░ ░▒ ▒░ ░ ░  ░ ░ ▒  ▒  ▒ ░░ ░░   ░ ▒░    ░     ░ ░  ░ ▒ ░   ║    
║    ▒ ░     ▒ ░   ░   ░ ░ ░ ░░ ░    ░    ░ ░  ░  ▒ ░   ░   ░ ░   ░         ░    ▒ ░   ║    
║    ░       ░           ░ ░  ░      ░  ░   ░     ░           ░               ░  ░ ░   ║      
║                                         ░                                            ║
║                                                                                      ║
║            ⚡⚡⚡ LinkedIn Profile Extraction The Lazy Way ⚡⚡⚡                          ║
║                                   by @two06                                          ║
║                                                                                      ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
```

LinkedIn recon the easy way. 

## What it does

LinkedIntel sits in the background while you browse LinkedIn via Burp and automatically extracts profile information from the API responses. 

## Installation

1. Download `linkedintel.py`
2. Fire up Burp Suite
3. Go to **Extender** → **Extensions** → **Add**
4. Select **Python** and point it at the downloaded file
5. Watch the sick ASCII art load
6. Start collecting souls

## Usage

### The Lazy Way (Recommended)
1. Enable "Auto-extract profiles" in the Settings tab
2. Browse LinkedIn through Burp's proxy
3. Do literally anything else while profiles get harvested
4. Export when you're done

### The Manual Way  
Right-click any LinkedIn response and select "Extract LinkedIn Profiles".

### Settings
- **Auto-extract** - Toggle automatic harvesting
- **Auto-save** - Dump profiles to CSV automatically  
- **Debug logging** - See what's happening under the hood
- **Output directory** - Where your stolen data goes

## What gets extracted

- Full names (real ones, not "LinkedIn Member")
- Job titles and positions
- Geographic locations
- Profile URLs for follow-up stalking
- Premium badges and verification status
- Profile summaries when visible
- Timestamps for your records

## Output

Profiles get saved as CSV files with all the good stuff:

```csv
Name,Position,Location,Profile URL,Badge,Summary,Timestamp
"John Target","Senior Engineer","San Francisco, CA","https://linkedin.com/in/johntarget","Premium","Builds stuff...","2024-01-15 14:30:22"
```

## Target APIs

The extension monitors LinkedIn's GraphQL endpoints:
- `/voyager/api/graphql` - Main search results
- `/voyager/api/search` - Alternative search paths
- Any other LinkedIn API traffic it encounters

## Contributing

Found a bug? LinkedIn changed their API again? PRs welcome.

---
