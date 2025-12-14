

import os

##### email Service Configuration (SMTP) ######
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_USE_TLS = True  # Use TLS for Gmail
EMAIL_USE_SSL = False  # Set SSL to False
EMAIL_PORT = 587  # Gmail SMTP port for TLS
EMAIL_HOST_USER = 'info@geminiplanetarium.com'
EMAIL_HOST_PASSWORD = 'Alok@6199'  # Use an app-specific password from Gmail

