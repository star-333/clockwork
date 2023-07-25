from setuptools import setup

setup(
    name = 'clockwork',
    version = '0.2.0',
    py_modules = ['clockwork', 'timing', 'convert'],
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