# Integracja Systemów – (Flask + MySQL)


docker compose up --build -d      # build + run
docker compose exec app python -m app.cli   # create tables once

link:
http://localhost:5000

In Visual Studio Code just download DevDb by Damilola Olowookere, press Ctrl + K + D, and you’ll see the database.

Tables:

docker compose exec -T app python - <<'PY'
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    tables = db.session.execute(text("SHOW TABLES;")).scalars().all()
    print("Tables in MySQL:", tables)
PY



# Opens the MySQL prompt
docker compose exec db mysql -uapp -papp integracja

SHOW TABLES;
DESCRIBE region;
SELECT * FROM housing_price WHERE quarter='2025';
UPDATE interest_rate SET value=3.00 WHERE year(rate_date)=2020;
DELETE FROM property_type WHERE name='old_type';
EXIT;
