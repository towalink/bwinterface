import os
import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()

setup_kwargs = {
    'name': 'bwinterface',
    'version': '0.2.0',
    'author': 'Dirk Henrici',
    'author_email': 'towalink.bwinterface@henrici.name',
    'description': 'access the Bitwarden/Vaultwarden CLI ("bw") conveniently',
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
    'url': 'https://www.github.com/towalink/bwinterface',
    'packages': setuptools.find_namespace_packages('src'),
    'package_dir': {'': 'src'},
    'classifiers': [
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology'
    ],
    'python_requires': '>=3.7',
    'keywords': 'Bitwarden Vaultwarden wrapper interface',
    'project_urls': {
        'Repository': 'https://www.github.com/towalink/bwinterface',
        'PyPi': 'https://pypi.org/project/bwinterface/'
    },
}


if __name__ == '__main__':
    setuptools.setup(**setup_kwargs)
