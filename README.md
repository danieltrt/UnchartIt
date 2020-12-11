# UnchartIt: An Interactive Framework for Program Recovery from Charts

## Source code:
Source code for synthesizer: UnchartIt/web/synth/src/ \
Source code for distinguisher: UnchartIt/web/dist/src/ \
Source code for neural network: UnchartIt/web/data/src/


## How to run the web interface:

**Create a virtual environment (Python 3.7):**

`python3 -m venv venv`\
`source venv/bin/activate`

**Requirements**:\
`pip3 install django==3.0.6`\
`pip3 install click==7.1.2`\
`pip3 install matplotlib==3.2.1`\
`pip3 install numpy==1.18.4`\
`pip3 install tensorflow==1.14.0`\
`pip3 install keras==2.2.5`\
`pip3 install efficientnet==1.1.0`

**External requirements**:\
Model checker: C Bounded Model Checker (CBMC)\
Sat solver: open-wbo (sat solver of your choice)

**How to run locally:**\
`cd web`\
`python3 manage.py migrate` (creates a local DB)\
`python3 manage.py runserver`
