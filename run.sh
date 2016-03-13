#!/usr/bin/env bash
sudo uwsgi -s /tmp/uwsgi.sock -w todays_dinner:app --uid www-data --gid www-data
