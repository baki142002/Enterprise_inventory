# Web-Based — Enterprise Inventory Tracking & Demand Forecasting

A Django starter application for the project titled **Web-Based Automated Inventory Tracking and Predictive Demand Forecasting System for Enterprise Operations**.

## Included modules
- Login/logout using Django authentication
- Dashboard with product count, low-stock count, inventory value, and recent sales
- Product, category, and supplier management
- Stock-in, stock-out, and adjustment transactions
- Sales recording with automatic stock deduction
- Low-stock monitoring
- 30-day demand estimate based on the previous 30 days of sales
- Suggested reorder quantity
- Sales and transaction history
- Django admin for administrative data management

## Requirements
- Python 3.10+
- pip

## Setup (Windows)
1. Extract the ZIP file.
2. Open Command Prompt or PowerShell inside the extracted `enterprise_inventory_system` folder.
3. Create a virtual environment:

   ```bash
   py -m venv venv
   venv\\Scripts\\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create database tables:

   ```bash
   python manage.py migrate --run-syncdb
   ```

6. Create your administrator login:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

8. Open http://127.0.0.1:8000/ and sign in using the superuser credentials.

## Setup (macOS/Linux)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py createsuperuser
python manage.py runserver
```

## Database
SQLite is configured by default and creates `db.sqlite3` in the project folder. For PostgreSQL, install `psycopg[binary]`, set `DB_ENGINE=postgres`, and provide `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` environment variables.

## Important notes
- This is a functional academic/prototype starter, not a production-hardened enterprise deployment.
- The forecasting module currently uses a simple baseline: sales quantity over the last 30 days projected over the next 30 days. It is deliberately transparent and should not be described as a trained AI model.
- For production, add role-based permissions, automated tests, audit controls, backups, HTTPS, secure environment secrets, pagination, CSV import/export, and a more advanced forecasting model once sufficient historical data exists.
- `StockTransaction` adjustments set the product's on-hand quantity to the entered quantity. Stock-in and stock-out add or subtract the entered quantity.
