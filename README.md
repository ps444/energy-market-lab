# Energy Market Lab

Python tools for modelling and analysing power markets, starting with a UK half-hourly price generator.

## What it does

`main.py` generates a day of synthetic electricity prices for the UK or France, at hourly or half-hourly settlement resolution.

- **Settlement periods follow the clock changes.** A normal day has 24 hourly or 48 half-hourly periods. The spring clock-change day has 23 or 46, and the autumn one has 25 or 50. Each period is labelled with its local clock time, so on the autumn day the repeated hour appears twice (UK: 01:00, 01:00) and on the spring day the skipped hour is missing.
- **Prices follow realistic patterns.** Each price is a base price multiplied by seasonal, day-of-week and time-of-day factors, plus random noise.
- **It compares two generation methods.** A plain Python loop and NumPy are timed against each other. The built-in timing is a single rough run; see the [development log](#stage-1-random-prices-loop-vs-numpy) for a proper comparison.

## Quick start

Built on Python 3.12; tested on Python 3.14.

```bash
pip install -r requirements.txt
python main.py 2026-10-25 hh UK
```

The arguments are:

| Argument | Values |
|---|---|
| Date | `YYYY-MM-DD` |
| Granularity | `hourly` / `h` or `half-hourly` / `hh` |
| Location | `UK` or `France` |

Sample output for the UK autumn clock-change day (prices are random, so yours will differ):

```
DST Status: long day
Generating 25 periods...

Period     Realistic       Random          Pattern
00:00      £27.20          £1.54           Night (Low)
01:00      £30.85          £13.76          Night (Low)
01:00      £31.75          £9.20           Night (Low)
...
```

## How the model works

```
price = base price × seasonal × day-of-week × time-of-day × random (±10%)
```

| Factor | Values |
|---|---|
| Base price | 50 |
| Season | Winter 1.5, Spring 1.0, Summer 0.8, Autumn 1.1 |
| Day of week | Weekday 1.1, Weekend 0.9 |
| Time of day | Night (00:00–06:00) 0.6, Morning peak (06:00–09:00) 1.2, Daytime (09:00–17:00) 1.0, Evening peak (17:00–21:00) 1.4, Late evening (21:00–24:00) 0.8 |

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The clock-change tests don't check the code against itself. They compare every period's local start time with Python's time-zone database (`zoneinfo`), for the UK and France, hourly and half-hourly, on the spring, autumn and a normal day in each year from 2024 to 2027.

## Limitations

- **The prices are synthetic.** The multipliers were chosen by hand to show the typical shape of a day, week and year. They are not estimated from market data.
- **Only the UK and France are supported**, using the current European clock-change rule (last Sunday of March and October).
- **No price spikes, negative prices or volatility clustering**, all of which real power prices show.

## Roadmap (planned)

1. Pull real day-ahead prices and measure daily price spreads.
2. Estimate the model's multipliers from real prices instead of choosing them by hand.
3. Model the arbitrage revenue a battery could earn from those spreads.

## Development log

How the generator was built, step by step.

### Stage 1: Random prices, loop vs NumPy

The first version generated random prices two ways, to compare their performance:

- `price_generator_for1.py`: a loop using Python's built-in `random` library.
- `price_generator_for2.py`: NumPy's vectorised random number generation.

**Fixes along the way:**

- Removed stray semicolons at the ends of lines.
- Prices were originally returned as text with a "£" in front. Text can't be used in calculations (`"£47.38" + "£52.10"` doesn't add up), so the generators now return numbers and the "£" is only added when printing.

**Observations:**

- The loop runs faster when results are added to a list and returned, rather than printed inside the loop. Returning values also makes the function reusable.
- After the Stage 2 changes, the loop version appeared faster than NumPy.
- **Re-checked later, and that result didn't hold.** `main.py` times a single run with `datetime.now()`, which is too coarse for code that takes microseconds. Timing repeated runs with `timeit` showed NumPy faster at both sizes on my machine: about 7 µs vs 27 µs for 48 prices, and about 4.5 ms vs 62 ms for 100,000.

### Stage 2: Dates, granularity, location and clock changes

The script was changed to take a date, a granularity and a location instead of a number of prices:

1. Replaced the single `num = int(sys.argv[1])` argument with three inputs: date, granularity and location.
2. Added granularity logic: 24 hourly or 48 half-hourly settlement periods.
3. Printed the inputs back so they could be checked.
4. Generated prices for each settlement period to check prices were actually being returned.
5. Added clock-change (DST) handling: `find_last_sunday()` finds the last Sunday of March and October, and `is_dst_day()` classes the date as a short, long or normal day.

These steps were arrived at through iterative errors.

### Stage 3: Realistic price patterns

Added `generate_realistic_prices()`, which builds each price from multipliers (see [How the model works](#how-the-model-works)):

1. Start with a base price, chosen arbitrarily.
2. Apply a seasonal multiplier: European power prices are generally higher in winter than in summer.
3. Apply a time-of-day multiplier: higher at the morning and evening peaks, lower overnight.
4. Apply a day-of-week multiplier: weekdays have higher demand than weekends.
5. Apply a random multiplier to simulate day-to-day variation.

### Stage 4: Clock-change fix and France

Periods were labelled by counting elapsed time from midnight, so on clock-change days every period after the change was an hour out. The time-of-day profile used the same calculation, so the price shape was shifted too. Added `period_start_time()` to convert each period to its local clock time. Added France, which changes clocks on the same days as the UK but an hour later in local time. Added tests that check every period against Python's time-zone database.
