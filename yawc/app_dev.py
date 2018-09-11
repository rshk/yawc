from .app import create_app, setup_logging

setup_logging()

app = create_app()
app.debug = True
