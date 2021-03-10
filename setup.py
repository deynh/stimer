import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simpletimer",
    version="0.1.0",
    author="Nicholas DeYarman",
    author_email="ndeyarman@tutanota.com",
    description=(
        'Simpletimer is a command line timer that features short "fuzzy" '
        "syntax and basic output."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deynh/simpletimer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=["progressbar2"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "stimer=simpletimer.__main__:main",
            "simpletimer=simpletimer.__main__:simpletimer",
        ],
    },
)
