from setuptools import setup

setup(
    name = "White Morgan Capital Management",
    version = "0.0.1",
    author = "Chris White, Daniel Morgan",
    author_email = "white.cdw@gmail.com, daniel.freetime@gmail.com",
    description = ("Makin dolla billz look easy"),
    keywords = "",
    url = "https://github.com/moody-marlin/wmcm.git",
    install_requires = ['datetime',
	'pandas',
	'numpy',
	'pandas_datareader'],
    packages=['wmcm'],
)
