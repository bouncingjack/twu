import setuptools
import os
import json
import semver
import twlog
from pathlib import Path


logger = twlog.TimeWatchLogger()


def write_params_file(params_file_path, params_default):
    if not os.path.exists(os.path.dirname(params_file_path)):
        Path(os.path.dirname(params_file_path)).mkdir(parents=True, exist_ok=True)
    with open(params_file_path, 'w+') as f:
        f.write(json.dumps(params_default, indent=4))


logger.info('Staring install')

with open("README.md", "r") as fh:
    long_description = fh.read()

params_default = {
    'params_version': "1.0.0",
    'download_dir': os.path.join(os.path.expanduser('~'), 'Downloads'),
    'user': {
        'company': 'xxx',
        'worker': 'yyy',
        'pswd': 'zzz'
    },
    'work': {
        'location': {
            'lat': 55.555555,
            'long': 66.666666
        },
        'weekend': ['Friday', 'Saturday'],
        'work_day': {
            'randomize': True,
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

logger.info('Installing parameters file')
expected_params_version = '1.0.0'
if os.path.exists(params_file_path):
    with open(params_file_path, 'r') as f:
        try:
            params_version = semver.Version(json.loads(f.read())['params_version'])
            logger.info('Detected parameters file version {}'.format(params_version))
            if not params_version == semver.Version(expected_params_version):
                logger.info('This version requires parameters file version {}. Creating a default one'.format(
                    expected_params_version))
                os.rename(params_file_path, os.path.join(os.path.dirname(params_file_path), 'params_archive.json'))
                write_params_file(params_file_path, params_default)
        except json.decoder.JSONDecodeError:
            logger.info('parameters file too old - no version. Creating default')
            f.close()
            os.rename(params_file_path, os.path.join(os.path.dirname(params_file_path), 'params_archive.json'))
            write_params_file(params_file_path, params_default)

else:
    logger.info('Parameters file not found, creating a default one')
    write_params_file(params_file_path, params_default)

logger.info('Installing dependencies')
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

