from distutils.core import setup

import cosmos

setup(
    
    name='cosmos',
    version=cosmos.__version__,
    description='A Simple MOM middleware written in python',
    long_description=cosmos.__doc__,
    license=cosmos.__license__,
    url='https://github.com/vyscond/cosmos',

    author=cosmos.__author__,
    author_email='vyscond@gmail.com',

    py_modules=['cosmos','vylog','vysocket'],
    scripts=['moon.py'],
    install_requires=[ "netifaces == 0.8" ]
)
