import time
import displayio
from adafruit_magtag.magtag import MagTag
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
import adafruit_requests as requests

# Configuration
GITHUB_USER = "ehippy"
USE_FAKE_DATA = True  # Used for fast testing, skips networking
UPDATE_INTERVAL = 24 * 60 * 60  # Update once per day (24 hours)

# Create MagTag object
magtag = MagTag()

# Optimize for battery life
magtag.peripherals.neopixel_disable = True  # Turn off NeoPixels
if hasattr(magtag.peripherals, 'light_sensor_disable'):
    magtag.peripherals.light_sensor_disable = True  # Turn off light sensor

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
        
        # Extract contribution counts and stats from the response
        contributions = []
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        total_contributions = data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
        
        for week in weeks:
            for day in week['contributionDays']:
                contributions.append(day['contributionCount'])
        
        # Calculate current streak and best day from the data
        best_day = max(contributions) if contributions else 0
        
        current_streak = 0
        for count in reversed(contributions):
            if count > 0:
                current_streak += 1
            else:
                break
        
        print(f"Fetched {len(contributions)} days of contribution data")
        print(f"Total: {total_contributions}, Streak: {current_streak}, Best: {best_day}")
        
        # Return data as tuple: (contributions, total, streak, best)
        return (contributions, total_contributions, current_streak, best_day)
        
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
    weeks = 32  # ~7.5 months, fills width
    days_per_week = 7
    cell_width = 8
    cell_height = 8
    gap = 1
    
    # Calculate starting position at top of screen
    graph_width = weeks * cell_width + (weeks - 1) * gap
    graph_height = days_per_week * cell_height + (days_per_week - 1) * gap
    start_x = (display_width - graph_width) // 2
    start_y = 3  # Top margin
    
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
    for i in range(224):  # 32 weeks
        # Create varied data: mostly low activity with some busy days
        if i % 7 == 0 or i % 7 == 6:  # Weekends - less activity
            contributions.append(random.randint(0, 2))
        elif i % 30 < 5:  # First week of month - busy
            contributions.append(random.randint(10, 25))
        else:  # Regular days
            contributions.append(random.randint(0, 15))
    print(f"Generated {len(contributions)} days of fake data")
    
    # Calculate fake stats
    total = sum(contributions)
    best = max(contributions)
    streak = 0
    for count in reversed(contributions):
        if count > 0:
            streak += 1
        else:
            break
else:
    # Fetch real data from GitHub
    result = fetch_contribution_data()
    if not result:
        print("Failed to fetch data, falling back to fake data")
        import random
        contributions = []
        for i in range(224):
            if i % 7 == 0 or i % 7 == 6:
                contributions.append(random.randint(0, 2))
            elif i % 30 < 5:
                contributions.append(random.randint(10, 25))
            else:
                contributions.append(random.randint(0, 15))
        total = sum(contributions)
        best = max(contributions)
        streak = 0
        for count in reversed(contributions):
            if count > 0:
                streak += 1
            else:
                break
    else:
        contributions, total, streak, best = result

print(f"Stats - Streak: {streak}, Total: {total}, Best: {best}")

# Draw the graph
draw_contribution_graph(contributions)

# Calculate pill dimensions for positioning
pill_width = len(GITHUB_USER) * 6 + 12
pill_center_x = 2 + pill_width // 2

# Add GitHub logo centered above username, overlapping 4px into pill
try:
    bitmap = displayio.OnDiskBitmap("/github-logo.bmp")
    palette = bitmap.pixel_shader
    palette.make_transparent(0)  # Make background transparent
    logo_x = pill_center_x - 20  # Center 40px logo
    logo_y = 113 - 40 + 4  # 4px into the pill (pill starts at y=113)
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=logo_x, y=logo_y)
    magtag.graphics.splash.append(tile_grid)
    print("GitHub logo added")
except Exception as e:
    print(f"Could not load logo: {e}")

# Add white rounded pill background for username
pill = RoundRect(
    2, 113,  # x, y position
    len(GITHUB_USER) * 6 + 14, 14,  # width, height (approx text width + more padding)
    5,  # corner radius
    fill=0xFFFFFF,
    outline=0x000000,
    stroke=1
)
magtag.graphics.splash.append(pill)

# Add small username label in bottom-left corner
username_index = magtag.add_text(
    text_position=(6, 126),
    text_scale=1,
    text_anchor_point=(0.0, 1.0)
)

# Add stats in bottom-right (numbers on top, labels below)
streak_num_index = magtag.add_text(
    text_position=(200, 105),
    text_scale=2,
    text_anchor_point=(0.5, 0.5)
)
streak_label_index = magtag.add_text(
    text_position=(200, 120),
    text_scale=1,
    text_anchor_point=(0.5, 0.5)
)
total_num_index = magtag.add_text(
    text_position=(250, 105),
    text_scale=2,
    text_anchor_point=(0.5, 0.5)
)
total_label_index = magtag.add_text(
    text_position=(250, 120),
    text_scale=1,
    text_anchor_point=(0.5, 0.5)
)
best_num_index = magtag.add_text(
    text_position=(290, 105),
    text_scale=2,
    text_anchor_point=(1.0, 0.5)
)
best_label_index = magtag.add_text(
    text_position=(290, 120),
    text_scale=1,
    text_anchor_point=(1.0, 0.5)
)

# Set all text with auto_refresh=False to batch the updates
magtag.set_text(f"@{GITHUB_USER}", index=username_index, auto_refresh=False)
magtag.set_text(str(streak), index=streak_num_index, auto_refresh=False)
magtag.set_text("streak", index=streak_label_index, auto_refresh=False)
magtag.set_text(str(total), index=total_num_index, auto_refresh=False)
magtag.set_text("total", index=total_label_index, auto_refresh=False)
magtag.set_text(str(best), index=best_num_index, auto_refresh=False)
magtag.set_text("best", index=best_label_index, auto_refresh=False)

# Now refresh once
magtag.refresh()

print("Display updated successfully!")

# Deep sleep to conserve battery (wake up in 24 hours to update)
print(f"Going to deep sleep for {UPDATE_INTERVAL} seconds (24 hours)...")
magtag.exit_and_deep_sleep(UPDATE_INTERVAL)
