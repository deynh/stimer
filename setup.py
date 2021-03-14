import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stimer",
    version="0.2.1",
    author="Nicholas DeYarman",
    author_email="ndeyarman@tutanota.com",
    description=(
        'stimer stands for "simpletimer" and is a command line timer that features '
        'short "fuzzy" syntax and basic output.'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deynh/stimer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=["progressbar2"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["stimer=stimer.__main__:main"],
    },
)
