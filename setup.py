from setuptools import setup

setup(
    name = 'clockwork',
    version = '0.0.2',
    py_modules = ['clockwork'],
    install_requires = [
        'Click>=8.1.0', 
        'zenlog>=1.1', 
        'pyperclip>=1.8.2'
    ],
    entry_points = {
        'console_scripts': [
            'clockwork = clockwork:cli',
        ],
    },
)