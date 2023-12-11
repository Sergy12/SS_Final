from website import create_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = create_app()

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['200 per day', '50 per hour','50 per minute'],
    strategy="fixed-window",
    storage_uri="memory://",
)

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
    
if __name__ == '__main__':
    context = ('mycert.crt', 'mykey.key')  # Ruta a tu certificado y clave
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)