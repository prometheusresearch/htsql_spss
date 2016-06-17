#
# Copyright (c) 2016, Prometheus Research, LLC
#


from setuptools import setup, find_packages


setup(
    name='htsql_spss',
    version='0.1.0',
    description='An HTSQL extension that adds basic IBM SPSS support.',
    long_description=open('README.rst', 'r').read(),
    keywords='htsql extension spss sav',
    author='Prometheus Research, LLC',
    author_email='contact@prometheusresearch.com',
    license='AGPLv3',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU Affero General Public License v3',
    ],
    url='https://bitbucket.org/prometheus/htsql_spss',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=True,
    include_package_data=True,
    entry_points={
        'htsql.addons': [
            'htsql_spss = htsql_spss:SPSSAddon',
        ],
    },
    install_requires=[
        'HTSQL>=2.3,<3',
    ],
)
