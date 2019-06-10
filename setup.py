from setuptools import setup

setup(name='riminder_resume_exporter',
      version='0.0.2',
      description='Riminder resume exporter.',
      url='https://github.com/Riminder/riminder-resumes-exporter',
      author='riminder',
      author_email='contact@rimider.net',
      license='MIT',
      install_requires=[
        'riminder'
      ],
      packages=['resume_exporter'],
      entry_points={
        'console_scripts': [
            'resumeExporter = resume_exporter.resume_exporter:main',
        ]
      },
      python_requires='>=3.5',
      zip_safe=False)
