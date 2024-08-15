#!/bin/bash
gunicorn --config config/gunicorn_conf.py main:app