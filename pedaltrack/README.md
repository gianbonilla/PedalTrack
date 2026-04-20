# PedalTrack — Bike Rental Management System

A staff-operated bike rental management system built with Python and SQLite.
No internet connection required. Runs fully local.

## Requirements

- Python 3.8 or higher (tkinter is included in standard Python)
- No external packages needed

## Setup & Run

```bash
# 1. Navigate to the project folder
cd pedaltrack

# 2. Run the application
python main.py
```

## Default Login

| Username | Password    | Role     |
|----------|-------------|----------|
| admin    | admin1234   | Admin    |
| analim   | cashier123  | Cashier  |
| rpascual | mech123     | Mechanic |

**Change passwords after first login via Staff > Edit account.**

## Project Structure

```
pedaltrack/
├── main.py                  # Entry point
├── app.py                   # App root, theme, navigation
├── pedaltrack.db            # SQLite database (auto-created on first run)
│
├── db/
│   ├── database.py          # All database queries
│   └── seed.py              # Default data seeded on first run
│
├── components/
│   ├── sidebar.py           # Navigation sidebar
│   └── widgets.py           # Shared UI helpers and constants
│
└── views/
    ├── login_view.py        # Login screen
    ├── dashboard_view.py    # Dashboard with stats and active rentals
    ├── customers_view.py    # Customer list + profile + add/edit
    ├── bikes_view.py        # Bike fleet management
    ├── rentals_view.py      # Rental list + new rental + return/payment
    ├── payments_view.py     # Payment history with totals
    ├── maintenance_view.py  # Maintenance log + add/edit records
    └── staff_view.py        # Staff accounts (admin only)
```

## Role Permissions

| Feature            | Admin | Cashier | Mechanic |
|--------------------|-------|---------|----------|
| Dashboard          | ✓     | ✓       | ✓        |
| Customers          | ✓     | ✓       |          |
| Bikes              | ✓     | ✓       | ✓        |
| Rentals            | ✓     | ✓       |          |
| Payments           | ✓     | ✓       |          |
| Maintenance        | ✓     |         | ✓        |
| Staff (admin only) | ✓     |         |          |

## Database

The database file `pedaltrack.db` is auto-created in the project root on first run.
All tables, indexes, and triggers are applied automatically.

To reset the database, delete `pedaltrack.db` and restart the app.
