import logging
import os

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from uvicorn import run

from pizzalibrary.startup import setup_telemetry

setup_telemetry("pizza-shop", "1")

logging.info("Starting application")

from pizza_shop.webapp import app

# already instrumented from Azure Distro: FastAPIInstrumentor.instrument_app(app)
print("Ready to serve")
port = int(os.getenv('PORT', 8000))
host = os.getenv('HOST', "0.0.0.0")
if os.getenv('DEBUG', 'false').lower() == 'true':
    run("pizza_shop.webapp:app", host=host, port=port, reload=True)
else:
    run(app, host=host, port=port, reload=False)
