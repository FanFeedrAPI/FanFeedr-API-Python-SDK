try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='fanfeedr',
    version='1.0',
    description='FanFeedr API Python SDK',
    author='FanFeedr Tech',
    author_email='tech@fanfeedr.com',
    url='http://developer.fanfeedr.com',
    install_requires=[
      "simplejson==2.1.6"
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'fanfeedr': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,
)

