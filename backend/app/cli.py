import click
from . import create_app, db

@click.command("create-tables")
def _create_tables():
    app = create_app()
    with app.app_context():
        db.create_all()
        click.secho("Tables created", fg="green")

if __name__ == "__main__":
    _create_tables()
