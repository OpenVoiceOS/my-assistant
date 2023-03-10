import os
import os.path

from setuptools import setup, find_packages

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def get_version():
    """ Find the version of ovos-core"""
    version = None
    version_file = os.path.join(BASEDIR, 'my_assistant', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


setup(
    name='my-assistant',
    version=get_version(),
    license='Apache-2.0',
    url='https://github.com/OpenVoiceOS/my-assistant',
    description='my voice assistant built on top of ovos-core',
    install_requires=required('requirements.txt'),
    packages=find_packages(include=['my_assistant*']),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={
        'console_scripts': [
            'my-assistant=my_assistant.__main__:main',
            # or use old style per-service launchers
            # 'my-speech-client=my_assistant.listener.__main__:main',
            # 'my-messagebus=my_assistant.bus.__main__:main',
            # 'my-skills=my_assistant.skills.__main__:main',
            # 'my-audio=my_assistant.audio.__main__:main',
            # 'my-gui-service=my_assistant.gui.__main__:main'
        ]
    }
)
