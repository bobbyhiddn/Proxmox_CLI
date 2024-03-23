from setuptools import setup, find_packages

setup(
    name='pxmx-cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'paramiko',
    ],
    entry_points='''
        [console_scripts]
        pxmx=pxmx.cli:cli
    ''',
    author="Your Name",
    author_email="your_email@example.com",
    description="A CLI for Proxmox management.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourgithub/Proxmox_CLI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
