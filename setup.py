import os

from setuptools import find_packages, setup


def gather_package_data_paths():
    package_data_paths = []

    # Reuse .gitignore to keep it in sync
    with open(".gitignore", "r", encoding="utf-8") as f:
        ignorelist = f.read().split("\n")

    for root, dirs, files in os.walk("wincpy"):
        for item in ignorelist:
            if item in dirs:
                dirs.remove(item)

        # Trim off 'wincpy/'
        root = root[7:]
        for filename in files:
            # We don't exclude non-Python files because then Python files that
            # are in a folder without __init__.py in it are omitted.
            package_data_paths.append(os.path.join(root, filename))
    return package_data_paths


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="wincpy",
    author="Winc Academy",
    author_email="wincacademy.com",
    description="Assists students in doing Winc Academy Python exercises.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://github.com/WincAcademy/wincpy-dist",
    project_urls={
        "Downloads": "https://github.com/WincAcademy/wincpy-dist/releases/latest",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">= 3.8",
    package_data={"wincpy": gather_package_data_paths()},
    entry_points={"console_scripts": ["wincpy=wincpy.__main__:console_entry"]},
    install_requires=["rich>=10.9.0"],
    use_scm_version={"version_file": "wincpy/_version.py"},
)
