# Code assistant
A python script that generates code and writes it to local files, using LangChain Agents and OpenAI's API.

It supports two alternative tool strategies: 
- FileSystem: it gives control over the file system for the script to change and insert code in files.
- RAG: it uses a LanguageParser, memory vectors and MMR RAG to provide openai with the right context, but it returns only the changes to the console.

## Setup
It requires the OPENAI_API_KEY environment variable to be set, which you can provide by creating an .env file:
```bash
echo 'OPENAI_API_KEY="..."' > .env
```

Also, remember to install the packages before running it:  
```bash
pip install -r requirements.txt
```


## Usage
```bash
python script.py "Add an authentication method to api.ts" -d "../project"
```

https://github.com/eactisgrosso/code-assistant/assets/2279003/878e5933-f886-43c5-b936-8e4efc9aad8e

Where the first argument is the command, and -d is the root directory where the files referred in the command are located.

Another example, now using 'RAG', which should be cheaper in terms of token consumption, and faster, but it won't update files automatically:
```bash
python script.py "Update api.py to add an endpoint '/delete_item'" -d "../project" -t RAG
```

https://github.com/eactisgrosso/code-assistant/assets/2279003/d36b9787-feac-4f98-8b94-0cc149862aab


