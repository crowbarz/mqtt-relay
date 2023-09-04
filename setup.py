"""mqtt_relay setup.py."""

import setuptools
from mqtt_relay.const import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mqtt_relay",
    version=VERSION,
    author="Crowbar Z",
    author_email="crowbarz@outlook.com",
    description="Monitor file changes and publish contents to MQTT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crowbarz/mqtt-relay",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: AsyncIO",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.6",
    install_requires=[
        "python-daemon==3.0.1",
        "paho-mqtt==1.6.1",
        "inotify-simple==1.3.5",
    ],
    entry_points={
        "console_scripts": [
            "mqtt-relay=mqtt_relay.mqtt_relay:main",
        ]
    },
)
