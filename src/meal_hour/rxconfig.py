import reflex as rx
import os

config = rx.Config(
    app_name="app",
    # Production settings for Cloud Run - everything on one port
    backend_host="0.0.0.0",
    backend_port=int(os.getenv("PORT", "8080")),
    # Remove frontend_port to serve frontend on backend_port
)