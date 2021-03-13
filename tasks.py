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
    os.system("poetry run isort mcanitexgen --settings-path pyproject.toml --profile black")
    os.system("poetry run isort tests --settings-path pyproject.toml --profile black")


@task
def test(c):
    os.system("poetry run pytest tests")


@task
def publish(c):
    os.system("poetry build")
    os.system("poetry publish")


@task
def coverage(c):
    os.system("poetry run coverage run -m pytest tests")
    os.system("poetry run coverage report")
    os.system("poetry run coverage-badge -o coverage.svg -f")
