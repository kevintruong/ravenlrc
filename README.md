# Youtube Creator service (Flask)
## install database 
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
sudo apt-get install mysql-client-core-5.7 
```


## run database sql 
```python
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
```

