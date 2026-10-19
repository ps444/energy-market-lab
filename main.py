# Import "datetime" library
from datetime import datetime, timedelta

# Import for access to terminal system
import sys


# Import functions I need
from price_generator_for1 import generate_random_number
from price_generator_for2 import generate_random_price_numpy

def find_last_sunday(year, month):

    """
    Find the day number of the last Sunday in a given month and year.

    For example: find_last_sunday(2023, 3) returns 26 (March 26, 2023 is last Sunday)
    """

    # Iterating backwards from last month
    if month == 12:
        # if December, then next month is January of new year
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        # Otherwise, go to first day of next month, then back one day
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)

    while last_day.weekday() != 6:
        last_day -= timedelta(days=1)

    return last_day.day

# Local hour at which the clocks change, per location.
# UK and France change on the same Sundays (both at 01:00 UTC), but local time differs:
#   UK:     spring 01:00 -> 02:00 (01:xx skipped),  autumn 02:00 -> 01:00 (01:xx repeated)
#   France: spring 02:00 -> 03:00 (02:xx skipped),  autumn 03:00 -> 02:00 (02:xx repeated)
CLOCK_CHANGE_HOUR = {"UK": 1, "FRANCE": 2}

# Currency used for display
CURRENCY = {"UK": "£", "FRANCE": "€"}


def is_dst_day(date_str, location):

    """
    Check if a given date is a DST change day for the specified location.

    Returns
        'short' if it's the spring forward day (lose one hour)
        'long' if it's the fall back day (gain one hour)
        'normal' if it's a normal day
    """

    if location.upper() not in CLOCK_CHANGE_HOUR:
        raise ValueError(f"Unsupported location '{location}'. Use 'UK' or 'France'.")

    # Convert string date to datetime object
    date = datetime.strptime(date_str, "%Y-%m-%d")
    year = date.year
    month = date.month
    day = date.day

    # UK and France both change clocks on the last Sunday of March and October
    # Find last Sunday in March (spring forward - SHORT day)
    march_last_sunday = find_last_sunday(year, 3)

    # Find last Sunday in October (fall back - LONG day)
    october_last_sunday = find_last_sunday(year, 10)

    if month == 3 and day == march_last_sunday:
        return 'short'
    elif month == 10 and day == october_last_sunday:
        return 'long'
    else:
        return 'normal'


def period_start_time(period, minutes_per_period, dst_type, location):

    """
    Convert a settlement period number into the local clock time it starts at.

    Periods count real elapsed time from midnight, so on clock-change days the
    local clock jumps: on a short day the change hour is skipped, on a long day
    it appears twice.

    For example, UK long day, hourly: periods 0, 1, 2, 3 start at 00:00, 01:00, 01:00, 02:00

    Returns (hour, minute)
    """

    elapsed = period * minutes_per_period
    change_minute = CLOCK_CHANGE_HOUR[location.upper()] * 60

    if dst_type == 'short' and elapsed >= change_minute:
        elapsed += 60   # Clocks jump forward an hour
    elif dst_type == 'long' and elapsed >= change_minute + 60:
        elapsed -= 60   # Clocks go back an hour

    return elapsed // 60, elapsed % 60


def time_function(func, parameter):
    # store current time in variable
    start_time = datetime.now()

    # Store result
    result = func(parameter)

    # store finished time in variable
    end_time = datetime.now()

    # calculate the time it took
    duration = end_time - start_time

    return { 
        'start_time': start_time, 
        'end_time': end_time, 
        'duration': duration,
        'prices': result
    } 

def generate_realistic_prices(date_str, num_periods, granularity, dst_type='normal', location='UK'):

    """
    Generate realistic energy prices with seasonality, daily, and weekly patterns.

    Args:
        date_str: Date in "YYYY-MM-DD" format
        num_periods: Number of periods to generate
        granularity: "hourly" or "half-hourly"
        dst_type: 'short', 'long' or 'normal' (from is_dst_day)
        location: "UK" or "France"

    Returns:
        List of realistic prices
    """

    import random

    # Parse the date
    date = datetime.strptime(date_str, "%Y-%m-%d")
    month = date.month
    day_of_week = date.weekday()    # 0=Monday, 6=Sunday

    # Base Price
    base_price = 50

    # 1. SEASONAL MULTIPLIER (Based on month)
    if month in [12, 1, 2]: # Winter (Dec, Jan, Feb)
        seasonal_mult = 1.5
    elif month in [6, 7, 8]:    # Summer (Jun, Jul, Aug)
        seasonal_mult = 0.8
    elif month in [3, 4, 5]:    # Spring (Mar, Apr, May)
        seasonal_mult = 1.0
    elif month in [9, 10, 11]:    # Autumn (Sep, Oct, Nov)
        seasonal_mult = 1.1
    
    # 2. WEEKLY MULTIPLIER (Based on day of week)
    if day_of_week < 5: # Monday - Friday (0-4)
        weekly_mult = 1.1
    else:   # Saturday - Sunday (5-6)
        weekly_mult = 0.9

    # 3. DAILY PROFILE MULTIPLIER (Based on time of day)
    prices = []

    # Determine minutes per period
    if granularity.lower() in ["hourly", "h"]:
        minutes_per_period = 60
    else:    # Half-Hourly
        minutes_per_period = 30

    # Generate prices for each period
    for period in range(num_periods):
        #   Calculate the local clock time this period starts at (allows for clock changes)
        hour, _ = period_start_time(period, minutes_per_period, dst_type, location)

        #   Time-of-day Multiplier
        if 0 <= hour < 6:   # Night Time (12am-6am)
            time_mult = 0.6
        elif 6 <= hour < 9:  # Morning Peak (6am-9am)
            time_mult = 1.2
        elif 9 <= hour < 17:  # Daytime (9am-5pm)
            time_mult = 1.0
        elif 17 <= hour < 21:  # Evening Peak (5pm-9pm)
            time_mult = 1.4
        else: # Late evening (9pm-12am)
            time_mult = 0.8

        # Random variation (+/- 10%)
        random_mult = random.uniform(0.9, 1.1)

        # Calculate final price
        price = base_price * seasonal_mult * weekly_mult * time_mult * random_mult

        # Round to 2 decimal places
        price = round(price, 2)

        prices.append(price)

    return prices


# === MAIN EXECUTION BLOCK ===
if __name__ == "__main__":
    # Get three separate input variable as arguments from command line
    date_input = sys.argv[1]    # e.g., "2023-10-29"
    granularity = sys.argv[2]   # e.g. "hourly" or "half-hourly"
    location = sys.argv[3]  # e.g., "UK"

    # Print these to check
    print(f"Date: {date_input}")
    print(f"Granularity: {granularity}")
    print(f"Location: {location}")
    print()

    # Confirm DST (also checks the location is supported)
    try:
        dst_type = is_dst_day(date_input, location)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

    currency = CURRENCY[location.upper()]

    # Calculate number of periods based on granularity and DST
    if granularity.lower() == "hourly" or granularity.lower() == "h":
        if dst_type == 'short':
            num_periods = 23    # Spring forward - lose hour - short day
        elif dst_type == 'long':
            num_periods = 25    # Fall back - gain hour - long day
        else:
            num_periods = 24    # Normal day

    elif granularity.lower() == "half-hourly" or granularity.lower() == "hh":
        if dst_type == 'short':
            num_periods = 46    # Spring forward - lose hour - short day
        elif dst_type == 'long':
            num_periods = 50    # Fall back - gain hour - long day
        else:
            num_periods = 48    # Normal day
        
    else:
        print(f"Error: Invalid granularity '{granularity}'. Use 'hourly' or 'half-hourly'.")
        sys.exit(1)

    print(f"DST Status: {dst_type} day")
    print(f"Generating {num_periods} periods...")
    print()

    # Generate realistic prices
    print("Generating realistic prices with seasonal, daily, and weekly patterns....")
    realistic_prices = generate_realistic_prices(date_input, num_periods, granularity, dst_type, location)

    # Also generate random prices for comparison
    print("Generating random prices for comparison...")
    random_prices = generate_random_number(num_periods)

    # Show difference
    print()
    print("=" * 70)
    print("PRICE COMPARISON: Realistic vs Random")
    print("=" * 70)
    print(f"{'Period':<10} {'Realistic':<15} {'Random':<15} {'Pattern':<30}")
    print("=" * 70)

    # Show first 10 periods to see the pattern
    for i in range(min(10, num_periods)):
        # Calculate the local clock time this period starts at (allows for clock changes)
        if granularity.lower() in ["hourly", "h"]:
            minutes_per_period = 60
        else:
            minutes_per_period = 30

        hour, minute = period_start_time(i, minutes_per_period, dst_type, location)
        time_str = f"{hour:02d}:{minute:02d}"

        # Determine pattern description
        if 0 <= hour < 6:
            pattern = "Night (Low)"
        elif 6 <= hour < 9:
            pattern = "Morning Peak (High)"
        elif 9 <= hour < 17:
            pattern = "Daytime (Medium)"
        elif 17 <= hour < 21:  
            pattern = "Evening Peak (Very High)"
        else: #  (9pm-12am)
            pattern = "Late Evening (Medium)"

        print(f"{time_str:<10} {currency}{realistic_prices[i]:<14.2f} {currency}{random_prices[i]:<14.2f} {pattern:<30}")
    
    print("=" * 70)
    print()
    
    # Show statistics
    realistic_avg = sum(realistic_prices) / len(realistic_prices)
    random_avg = sum(random_prices) / len(random_prices)
    realistic_min = min(realistic_prices)
    realistic_max = max(realistic_prices)
    random_min = min(random_prices)
    random_max = max(random_prices)
    
    print("STATISTICS:")
    print(f"Realistic prices - Avg: {currency}{realistic_avg:.2f}, Min: {currency}{realistic_min:.2f}, Max: {currency}{realistic_max:.2f}")
    print(f"Random prices    - Avg: {currency}{random_avg:.2f}, Min: {currency}{random_min:.2f}, Max: {currency}{random_max:.2f}")
    print()

    # Run both methods  
    first_example = time_function(generate_random_number, num_periods)
    second_example = time_function(generate_random_price_numpy, num_periods)

    # Show timing results
    print(f"Method 1 (random module) took: {first_example['duration']}")
    print(f"Method 2 (NumPy) took: {second_example['duration']}")
    print()


    # use if else statement to check which one is faster...
    if first_example['duration'] > second_example['duration']:
        print("Method 2 (NumPy) is faster")
    elif second_example['duration'] > first_example['duration']:
        print("Method 1 (random module) is faster")

    print()
    print(f"First 5 prices from Method 2: {second_example['prices'][:5]}")