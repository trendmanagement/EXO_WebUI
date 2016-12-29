import os
DEBUG = True
#COMPRESS_ENABLED = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "hwhnti*d=5h88#e!41=e$)2n30^c6jh8*7dl%!j%u*b02d*^2+"
NEVERCACHE_KEY = "6n)ttz65b%51d%&x!qrt(*cqv4^jrawm-$e##um(&+vg^ww-19"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "db.sqlite3",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}

###################
# DEPLOY SETTINGS #
###################

# Domains for public site
ALLOWED_HOSTS = ["10.0.1.4"]

# These settings are used by the default fabfile.py provided.
# Check fabfile.py for defaults.

FABRIC = {
     "DEPLOY_TOOL": "rsync",  # Deploy with "git", "hg", or "rsync"
     "SSH_USER": "tmqrquant",  # VPS SSH username
     "HOSTS": ["10.0.1.4"],  # The IP address of your VPS
     "DOMAINS": ALLOWED_HOSTS,  # Edit domains in ALLOWED_HOSTS
     "REQUIREMENTS_PATH": "requirements.txt",  # Project's pip requirements
     "LOCALE": "en_US.UTF-8",  # Should end with ".UTF-8"
     "DB_PASS": "123as345Sjb3zsdaSADc",  # Live database password
     "ADMIN_PASS": "tmqradmin",  # Live admin user password
     "SECRET_KEY": SECRET_KEY,
     "NEVERCACHE_KEY": NEVERCACHE_KEY,
}
