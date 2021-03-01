import os
import shutil
from pathlib import Path

from invoke import task


@task
def setup(c):
    os.system("poetry lock -n")
    os.system("poetry install -n")
    os.system("poetry run pre-commit install")


@task
def format(c):
    os.system("poetry run black . --config pyproject.toml")
    os.system("poetry run isort . --settings-path pyproject.toml")


@task
def test(c):
    os.system("poetry run py -m pytest")
