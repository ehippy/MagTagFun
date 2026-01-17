import time
import displayio
from adafruit_magtag.magtag import MagTag
from adafruit_display_shapes.rect import Rect
import adafruit_requests as requests

# Configuration
GITHUB_USER = "ehippy"
USE_FAKE_DATA = False  # Set to False to fetch real data from GitHub
UPDATE_INTERVAL = 24 * 60 * 60  # Update once per day (24 hours)

# Create MagTag object
magtag = MagTag()

# GitHub API endpoint
GITHUB_API_URL = "https://api.github.com/graphql"

def fetch_contribution_data():
    """Fetch contribution data from GitHub GraphQL API"""
    try:
        print(f"Fetching contributions for {GITHUB_USER}...")
        
        # Import secrets for GitHub token
        try:
            from secrets import secrets
            github_token = secrets.get('github_token', '')
        except:
            print("No GitHub token found in secrets")
            return None
        
        if not github_token or github_token == 'your_github_personal_access_token':
            print("Please add a valid GitHub token to secrets.py")
            return None
        
        # Connect to WiFi
        print("Connecting to WiFi...")
        magtag.network.connect()
        print("Connected!")
        
        # GraphQL query for contribution data
        query = """
        {
          user(login: "%s") {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
          }
        }
        """ % GITHUB_USER
        
        import json
        
        # Make the GraphQL POST request
        print("Fetching GitHub data...")
        response = magtag.network._wifi.requests.post(
            GITHUB_API_URL,
            headers={
                "Authorization": f"bearer {github_token}",
            },
            json={"query": query}
        )
        
        data = response.json()
        
        # Extract contribution counts from the response
        contributions = []
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        
        for week in weeks:
            for day in week['contributionDays']:
                contributions.append(day['contributionCount'])
        
        print(f"Fetched {len(contributions)} days of contribution data")
        return contributions
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        import sys
        sys.print_exception(e)
        return None

def draw_contribution_graph(contributions):
    """Draw the contribution graph on the MagTag display"""
    # MagTag display is 296x128 pixels
    display_width = 296
    display_height = 128
    
    # Title is already added in main, skip adding it again here
    
    if not contributions or len(contributions) == 0:
        print("No contributions data!")
        return
    
    print(f"Drawing graph for {len(contributions)} days of data")
    
    # Calculate max contributions for color scaling
    max_contrib = max(contributions) if contributions else 1
    if max_contrib == 0:
        max_contrib = 1
    
    print(f"Max contribution count: {max_contrib}")
    
    # Graph settings
    weeks = 17  # ~4 months, fills screen
    days_per_week = 7
    cell_width = 16
    cell_height = 16
    gap = 1
    
    # Calculate starting position to fill screen with minimal margins
    graph_width = weeks * cell_width + (weeks - 1) * gap
    graph_height = days_per_week * cell_height + (days_per_week - 1) * gap
    start_x = (display_width - graph_width) // 2
    start_y = 3  # Small top margin
    
    print(f"Graph position: x={start_x}, y={start_y}, width={graph_width}, height={graph_height}")
    
    # Draw contribution squares (weekly columns)
    week_data = []
    for i in range(0, len(contributions), days_per_week):
        week_data.append(contributions[i:i + days_per_week])
    
    # Limit to last 52 weeks
    if len(week_data) > weeks:
        week_data = week_data[-weeks:]
    
    print(f"Drawing {len(week_data)} weeks...")
    
    rect_count = 0
    for week_idx, week in enumerate(week_data):
        for day_idx, count in enumerate(week):
            x = start_x + week_idx * (cell_width + gap)
            y = start_y + day_idx * (cell_height + gap)
            
            # Determine color based on contribution count
            # E-ink display: 0x000000 = black, 0xFFFFFF = white
            if count == 0:
                color = 0xEEEEEE  # Very light gray (barely visible)
            elif count <= max_contrib * 0.25:
                color = 0xAAAAAA  # Light gray
            elif count <= max_contrib * 0.5:
                color = 0x777777  # Medium gray
            elif count <= max_contrib * 0.75:
                color = 0x333333  # Dark gray
            else:
                color = 0x000000  # Black
            
            rect = Rect(x, y, cell_width, cell_height, fill=color)
            magtag.graphics.splash.append(rect)
            rect_count += 1
    
    print(f"Drew {rect_count} rectangles!")

# Main execution
print("GitHub Contribution Graph for MagTag")
print("=" * 40)

# Fetch or generate contribution data
if USE_FAKE_DATA:
    # Generate fake data for testing
    print("Generating fake contribution data...")
    import random
    contributions = []
    for i in range(119):  # 17 weeks
        # Create varied data: mostly low activity with some busy days
        if i % 7 == 0 or i % 7 == 6:  # Weekends - less activity
            contributions.append(random.randint(0, 2))
        elif i % 30 < 5:  # First week of month - busy
            contributions.append(random.randint(10, 25))
        else:  # Regular days
            contributions.append(random.randint(0, 15))
    print(f"Generated {len(contributions)} days of fake data")
else:
    # Fetch real data from GitHub
    contributions = fetch_contribution_data()
    if not contributions:
        print("Failed to fetch data, falling back to fake data")
        import random
        contributions = []
        for i in range(119):
            if i % 7 == 0 or i % 7 == 6:
                contributions.append(random.randint(0, 2))
            elif i % 30 < 5:
                contributions.append(random.randint(10, 25))
            else:
                contributions.append(random.randint(0, 15))

# Draw the graph
draw_contribution_graph(contributions)

# Force display refresh
print("Refreshing display...")
magtag.graphics.display.refresh()

print("Display updated successfully!")

# Keep display on for testing
print("Keeping display on...")
while True:
    time.sleep(1)
