from setuptools import setup
import obvs


def version():
    s = []
    for num in obvs.__version__:
        s.append(str(num))
    return '.'.join(s)


setup(
    name='obvs.py',
    version=version(),
    packages=['obvs'],
    url='',
    license='',
    author='Christopher Read',
    author_email='',
    description='Python implementation of Obvs microservicebus library'
)
