# Python tools for modelling and analysing power markets, starting with a UK half-hourly price generator.

Overview

This project contains Python scripts demonstrating two methods to generate random prices:
    
    Using Python's built-in random library with a simple loop.
    Using the optimized NumPy library for fast random number generation.

The goal is to compare their performance and understand the differences. This is the perfect starting point because:
    
    It teaches about performance measurement.
    It introduces different Python Libraries
    It helps to build good habits around benchmarking.

Requirements

Python 3.12.2 installed

NumPy library (only for the NumPy-based generator)

    Install NumPy with:
    pip install numpy

How to Run

    Run the main script with a command-line argument specifying how many prices to generate:

For Example:

    python main.py 1000
    This will generate 1000 random prices using both methods and report how long each one took.

Project Structure

    price_generator_for1.py — Loop-based generator using Python’s random.
    price_generator_for2.py — NumPy-based generator.
    main.py — Runs both generators, measures execution time, and compares speed.

Sample Output

You should see output like this:

    Loop-based approach took: 0:00:03.456789
    NumPy-based approach took: 0:00:00.123456
    NumPy-based approach is faster

Notes

The generate_random_number() function in price_generator_for1.py currently returns prices formatted with "£", suitable for display.

    Updates to price_generator_for1.py include:
    removing the semicolon at the ends of the first two lines.
    removing the String(text) so the '£' is removed

Why This Matters

    String(text) Can't do Maths with them in Python "£47.38 + £52.10" does not work
    Random numbers lend themselves well to calculations

The NumPy generator returns raw floats, which can be formatted as needed.

Timing is done in the main script using a helper function to keep code clean.

The if _name_ == "_main_": structuring ensures proper script execution by.



Observations

    The Loop script runs more efficiently if:
    the output is simply added to a list or array.
    return is used instead of print for the output.
    This also means the script is more adaptable/versatile


Possible Next Steps

    Add more complexity - generate price curves, trends, scalability, seasonality, volatility
    Data Structures - store prices in pandas DataFrames
    Forward curves - build simple price curves
    Basic valuation - calculate present values, mark-to-market
    File I/O - read/write prices to csv/excel files

Next Steps
    
    Modify script to accept the following input:

    - Date: "2023-10-29"
    - Granularity: "hourly"(h) or "half-hourly"(hh)
    - Location: "UK" or "France"
    - Daylight Saving Time (DST)

    Modify script to simulate real-world patterns

    - Seasonality: Prices are generally higher in winter than in summer, for European countries
        There are two main seasons (pricing groups):
            
            Winter (December-February) - Prices are generally higher
            Summer (June-August) - Prices are generally lower
        
    - Daily Profile: Prices are higher during peak hours (e.g., morning and evening) and lower overnight
        There are four main price profiles during the day:

            Morning Peak (7am-9am) - High Demand>High Prices
            Daytime (9am-5pm) - Medium Prices
            Evening Peak (5pm-8pm) - High Demand>High Prices
            Night Time (11pm-6am) Low Prices

    - Weekly Profile: Weekday prices are typically higher than weekend prices.
        There are two main weekly profiles

            Weekdays (Mondays-Fridays) - Higher Demand>Higher Prices
            Weekends (Saturday-Sunday) -Lower Demand>Lower Prices

Next Steps Solution  

    Step 1: Modify input argument statements

    - Replace num = int(sys.arg[1]) with three separate inputs for date, daily profile/granularity, location
    - Delete import sys statements from modules price_generator_for1.py
    - Delete num = int(sys.argv[1]) from modules price_generator_for1.py, price_generator_for2.py

    Step 2: Add granularity logic
    - Calculate the number of periods based on "hourly" settlement periods
    - Hourly = 24 settlement periods ("h")

    Step 3: Print Output in the format 
    - Date: 2024-10-27
    - Granularity: half-hourly
    - Date: UK

    Observation
    - Above steps arrived at through iterative errors
    - Interstingly, at the end of these steps, price_generator_for1.py was faster.

    Step 4: Generate some prices based on settlement periods to test that prices are actually being returned

    Step 5: Add DST function

    Step 6: Add script for real-world prices
    - Create new function: generate_realistic_prices()
    
    Approach: Use Multipliers
        1) Start with a Base Price - Arbitrarily chosen here
        2) Apply Seasonal Multiplier - to calculate for the season
        3) Apply time-of-day Multiplier - to calculate for the day
        4) Apply day-of-week Multiplier - to calculate for the week
        5) Apply Randomness Multiplier - to simulate randomness
        
