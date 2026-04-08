import os
import time
import sys

import bolt

import bolt_flask
import behave_restful.bolt_behave_restful as br

bolt.register_module_tasks(bolt_flask)
bolt.register_module_tasks(br)

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'battleship')
TESTS_DIR = os.path.join(PROJECT_ROOT, 'tests')
FEATURES_DIR = os.path.join(PROJECT_ROOT, 'features')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')

bolt.register_task('ut', ['delete-pyc', 'delete-pyc.from-tests', 'shell.pytest'])
bolt.register_task('ct', ['conttest'])
bolt.register_task('ft', ['delete-pyc', 'start-flask', 'wait', 'behave-restful'])
bolt.register_task('cov', ['delete-pyc', 'delete-pyc.from-tests', 'shell.pytest.coverage'])


def wait(config, **_ignored):
    seconds = config.get('seconds', 0)
    time.sleep(seconds)

bolt.register_task('wait', wait)


config = {
    'delete-pyc': {
        'sourcedir': SRC_DIR,
        'recursive': True,
        'from-tests': {
            'sourcedir': TESTS_DIR,
        }
    },
    'shell': {
        'pytest': {
            'command': sys.executable,
            'arguments': ["-m", "pytest", TESTS_DIR],
            'coverage': {
                "arguments": [
                    "-m",
                    "pytest",
                    "--cov=battleship",
                    "--cov-report",
                    f"html:{OUTPUT_DIR}",
                    TESTS_DIR,
                ]
            }
        },
    },
    'conttest': {
        'task': 'ut',
        'directory': PROJECT_ROOT
    },
    'start-flask': {
        'startup-script': os.path.join(PROJECT_ROOT, 'app.py')
    },
    'behave-restful': {
        'directory': FEATURES_DIR,
        'definition': 'local',
    },
    'wait': {
        'seconds': 2,
    }
}
