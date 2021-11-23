import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="sxdm",
      version=read("VERSION.txt"),
      description="Tools for analyzing Scanning X-ray Diffraction Microscopy data",
      long_description=read('README.rst'),
      long_description_content_type='text/x-rst',
      author="William Judge",
      author_email="williamjudge94@gmail.com",
      url="https://github.com/WilliamJudge94/sxdm",
      keywords="SXDM X-ray microscopy APS 26-ID-C Argonne Advanced Photon Source",
      install_requires=[
          'h5py==2.8.0', 'matplotlib>=2.1.0', 'psutil',
          'numpy>=1.16.1', 'tqdm>=4.19.5', 'tifffile', 'miniutils>=1.0.1',
          'imageio>=2.5.0', 'nose>=1.3.7', 'progressbar>=2.5', 'scipy>=1.1.0',
          'opencv-python', 'PyQt5', 'pyparsing==2.4.7', 'docutils<0.18',
      ],
      python_requires='>=3.6',
      packages=['sxdm',],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.5',
          'Topic :: Scientific/Engineering :: Chemistry',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Scientific/Engineering :: Visualization',
      ]
)
