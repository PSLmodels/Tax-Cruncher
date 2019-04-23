import setuptools
import os

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="taxcrunch",
    version=os.environ.get("VERSION", "0.0.0"),
    author="Peter Metz",
    author_email="pmetzdc@gmail.com",
    description=(
        "Calculates federal tax liabilities from individual data under "
        "different policy proposals."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/peter-metz/Tax-Cruncher",
    packages=setuptools.find_packages(),
    install_requires=["taxcalc", "paramtools"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)