from setuptools import setup

setup(
    name="phase",
    version="1.1.0",
    description="Phase Ortho Aligners Class Structure",
    url="https://github.com/PhaseOrthoOrg/Phase-API/tree/main/services",
    author="Amber Price",
    author_email="amber@phaseortho.com",
    license="phaseortho",
    packages=["phase"],
    install_requires=["pyodbc"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Phase Ortho",
        "Operating System :: POSIX :: Windows/Linux",
        "Programming Language :: Python :: 3.7",
    ],
)
