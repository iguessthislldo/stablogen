from setuptools import setup

setup(
    name='stablogen',
    version='0.2',
    description='Jinja-based Static Blog Generator',
    url='https://github.com/iguessthislldo/stablogen',
    author='Fred Hornsey',
    author_email='fred@hornsey.us',
    license='MIT',
    install_requires=[
        'Jinja2',
        'arrow',
        'PyYAML',
        'Pygments',
    ],
    packages=['stablogen'],
    scripts=['bin/stablogen'],
    zip_safe=False
)
