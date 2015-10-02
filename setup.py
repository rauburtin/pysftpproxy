"""Setup configuration file."""

from setuptools import setup


def readme():
    """Open the readme."""
    with open('README.md') as f:
        return f.read()

setup(
    name='pysftpproxy',
    version='1.0.0',
    description='An OpenSSH SFTP Proxy wrapper in Python.',
    long_description=readme(),
    url='https://github.com/rauburtin/pysftpproxy',

    author="rauburtin",
    author_email="rauburtin@gmail.com",
    license='MIT',

    packages=['pysftpproxy'],
    scripts=['bin/pysftpproxy'],
    test_suite='nose.collector',
    tests_require=['nose', 'twisted','pycrypto','pyasn1'],

    install_requires=['twisted','pycrypto','pyasn1'],

    keywords=["pysftpproxy", "sftp", "openssh", "ssh", "proxy"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 6 - Mature",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Shells",
        "Topic :: System :: System Shells",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Utilities"
    ],

    zip_safe=False,
    include_package_data=True,
)
