# Code assistant
A python script that automates code modifications in various files using OpenAI's API.


## Setup
It requires the OPENAI_API_KEY environment variable to be set, which you can provide by creating an .env file:
```bash
echo 'OPENAI_API_KEY="..."' > .env
```

and installing the packages:  
```bash
pip install -r requirements.txt
```


## Usage
```bash
python script.py "Update api.py to add an endpoint '/delete_item'" -d "../project"
```

Where the first argument is the command, and -d is the root directory where the files referred in the command are located.
