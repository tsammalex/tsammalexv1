from setuptools import setup
import json


with open('metadata.json', encoding='utf-8') as fp:
    metadata = json.load(fp)


setup(
    name='lexibank_tsammalexv1',
    description=metadata['title'],
    license=metadata.get('license', ''),
    url=metadata.get('url', ''),
    py_modules=['lexibank_tsammalexv1'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'tsammalexv1=lexibank_tsammalexv1:Dataset',
        ]
    },
    install_requires=[
        'pylexibank>=2.7.0',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
