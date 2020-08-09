import setuptools
import os
import json

with open("README.md", "r") as fh:
    long_description = fh.read()

params_default = {
    'download_dir': os.path.join(os.path.expanduser('~'), 'Downloads'),
    'user': {
        'company': 'xxx',
        'worker': 'yyy',
        'pawd': 'zzz'
    },
    'work': {
        'location': {
            'lat': 55.555555,
            'long': 66.666666
        },
        'work_day': {
            'max_length': 1,
            'nominal_length': 1,
            'minimal_start_time': '07:00',
            'maximal_end_time': '23:59'
        }
    },
    'home': {
        'work_from_home_excuse_index': 9999
    },
    'holiday': {
        'holiday_eve_index': 9999,
        'holiday_eve_text': [],
        'holiday_index': 9999,
        'holiday_text': []
    }
}

params_file_path = os.path.join(os.path.dirname(__file__), 'params', 'params.json')

if not os.path.exists(params_file_path):
    with open(params_file_path, 'w+') as f:
        f.write(json.dumps(params_default, indent=4))

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
    dependencies = f.read().splitlines()

setuptools.setup(
    name="twu",
    version="1.0.0",
    author="Jack German",
    author_email="yakovger@gmail.com",
    description="Automatic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bouncingjack/twu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=dependencies
)