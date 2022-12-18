from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        # Needed to silence warnings (and to be a worthwhile package)
        name='x3word',
        url='https://github.com/jladan/package_demo',
        author='Agent X3',
        author_email='thepuzzlegang.agent@gmail.com',
        py_modules=['x3word'],
        # Needed to actually package something
        packages=find_packages(),
        # Needed for dependencies
        install_requires=['Pillow'],
        # *strongly* suggested for sharing
        version='1.0',
        # The license can be anything you like
        license='MIT',
        description='Crossword package that supports drawing words and keeping track of solved words and solvers, as well'
                    'as 4-directional word search. Needs an external json file to store the words and their definitions.',
        # Classifiers allow your Package to be categorized based on functionality
        classifiers=[
            "Programming Language :: Python :: 3.10",
            "Topic :: Games/Entertainment :: Puzzle Games",
            'Operating System :: OS Independent',
        ],
        # We will also need a readme eventually (there will be a warning)
        # long_description=open('README.txt').read(),
    )
