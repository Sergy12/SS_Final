from website import create_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = create_app()

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['200 per day', '50 per hour','5 per minute'],
    strategy="fixed-window",
    storage_uri="memory://",
)

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')