#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/top
/home/codespace/.python/current/bin/python manage.py backup_data
