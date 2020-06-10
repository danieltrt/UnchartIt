**Create a virtual environment (Python 3.8):**

`python3 -m venv venv`\
`source venv/bin/activate`

**Requirements**:\
`pip3 install django==3.0.6`\
`pip3 install click==7.1.2`\
`pip3 install matplotlib==3.2.1`\
`pip3 install numpy==1.18.4`\

**External requirements**:\
Model checker: C Bounded Model Checker (CBMC)\
Sat solver: open-wbo (sat solver of your choice)

**How to run locally:**\
`cd web`\
`python3 manage.py migrate` (creates a local DB)\
`python3 manage.py runserver`
