import os
import nox

ON_TRAVIS = os.environ.get("TRAVIS") == "true"

if not ON_TRAVIS:
    nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session):
    session.install("-r", "requirements/test.txt")
    session.run("black", "--check", "tapeworm", "tests", "noxfile.py")
    session.run("pylint", "tapeworm", "tests")


@nox.session
def tests(session):
    session.install("-r", "requirements/test.txt")
    session.run("pytest")


@nox.session
def watch(session):
    session.install("-r", "requirements/dev.txt")
    session.run("ptw", "--runner=pytest")


@nox.session
def run(session):
    session.install("-r", "requirements.txt")
    session.run("python", "dev.py")
