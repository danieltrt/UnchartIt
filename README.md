## **UnchartIt Distinguisher: A program distinguisher for program synthesis**


**Create a virtual environment (Python 3.8):**

`python3 -m venv venv`\
`source venv/bin/active`

**Requirements:**

`pip3 install click==7.1.2`


**External requirements:**

Model checker: C Bounded Model Checker (CBMC)\
Sat solver: open-wbo (sat solver of your choice)

**How to run locally:**

`python3 unchartit.py -d ./example/instance1.json -s open-wbo` 