import setuptools 

setuptools.setup(
    use_scm_version={
        'local_scheme': 'dirty-tag',
    },
    install_requires=['Twisted', 'ppb'],
)
