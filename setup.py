from setuptools import setup

setup(
    name='docbase-client',
    version='0.1.0',
    description='Python client for DocBase API.',
    url='https://github.com/kit494way/docbase-python-client',
    author='KITAGAWA Yasutaka',
    author_email='kit494way@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='docbase api client',
    install_requires=['requests'],
    python_requires='~=3.5',
    py_modules=['docbase'])
