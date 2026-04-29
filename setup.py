from setuptools import setup, find_packages

setup(
    name='file-compare-tool',
    version='0.1.0-alpha',
    packages=find_packages(exclude=['tests*']),
    description='A tool for easy comparison between tabular data.',
    url='https://github.com/provlab-bioinfo/file-compare-tool',
    author='Andrew Lindsay',
    author_email='andrew.lindsay@albertaprecisionlabs.ca',
    include_package_data=True,
    keywords=[],
    zip_safe=False,
    install_requires=[
        'pandas',
        'pyyaml',
        'tabulate',
        'pyyaml',
        'build',
        'pip'
    ],
    python_requires='>=3.11, <4'
)