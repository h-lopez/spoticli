import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spoticli-stormparticle", 
    version="1.20.0504",
    author="stormparticle",
    author_email="95hlopez@gmail.com",
    description="lightweight command line for spotify",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stormparticle/spoticli/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)