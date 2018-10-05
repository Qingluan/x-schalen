from setuptools import setup, find_packages
from setuptools.command.install import install
import os, sys
import time


class MyInstall(install):
    def run(self):
        install.run(self)
        os.rename("init.ini", os.path.expanduser("~/.config/x-schalen.ini"))
        if not os.path.exists(os.path.expanduser("~/.config/")):
            os.mkdir(os.path.expanduser("~/.config/"))

        if not os.path.exists(os.path.expanduser("~/.config/x-schalen")):
            os.mkdir(os.path.expanduser("~/.config/x-schalen"))

        if not os.path.exists(os.path.expanduser("~/.config/x-schalen/session-dbs/")):
            os.mkdir(os.path.expanduser("~/.config/x-schalen/session-dbs/"))
        


setup(name='x-mroy-11',
    version='0.0.0',
    cmdclass={"install": MyInstall},
    description='a manager in multiservers',
    url='https://github.com/Qingluan/x-mroy-11.git',
    author='Qing luan',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[ 'mroylib-min','tornado', 'qtornado',],
    entry_points={
        'console_scripts': [
            'x-conf=Factory.utils:conf_cmd',
        ]
    },

)
