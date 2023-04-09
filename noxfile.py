import nox


@nox.session
def tests(session):
    session.install(".")
    session.run("pytest", "tests")
