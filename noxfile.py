import nox


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.install(".")
    session.run("pytest", "tests")
