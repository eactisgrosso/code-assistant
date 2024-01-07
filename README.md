# Code assistant
A python script that generates code and writes it to local files, using LangChain Agents and OpenAI's API.

It supports two alternative tool strategies: 
- FileSystem: it gives control over the file system for the script to change and insert code in files.
- Retriever: it uses a LanguageParser, memory vectors and MMR RAG to provide the right context, but returns only the changes in the console.

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

Another example, with the 'Retriever' strategy:
```bash
python script.py "Update api.ts to consume this api 'https://example.com'" -d "../project" -t "Retriever"
```