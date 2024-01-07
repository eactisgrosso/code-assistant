import argparse
import os
import re
from typing import Literal
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import TerminalFormatter
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.tools.retriever import create_retriever_tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain.tools import tool


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MODEL = os.environ.get('MODEL', 'gpt-4-1106-preview')

@tool
def write_code(code: str, file_path: str):
    """It writes generated code to the specified file path"""

    print(f"Code to add/update in {file_path}: \n")

    lexer = guess_lexer(code)
    print(highlight(code, lexer, TerminalFormatter())) 

    return ""

def find_file_paths(root_directory: str, file_names: []):
    file_paths = []

    for dirpath, dirnames, filenames in os.walk(root_directory):
        for file in filenames:
            if file in file_names:
                full_path = os.path.join(dirpath, file)
                file_paths.append(full_path)

    return file_paths

file_pattern = r'\b\w+\.\w+\b'
def create_retriever_strategy_tool(command: str, root_dir: str):
    file_names = re.findall(file_pattern, command)
    file_paths = find_file_paths(root_dir, file_names)

    print("The following files will be used as context and/or code destination:\n", file_paths)

    code = []
    for file_path in file_paths:
        try:
            loader = GenericLoader.from_filesystem(
                file_path,
                glob="*",
                suffixes=[".py", ".js"],
                parser=LanguageParser(),
            )
            docs = loader.load()
            code.extend(docs) 
        except FileNotFoundError:
            print(f"File not found: {file_path}")


    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = DocArrayInMemorySearch.from_documents(code, embeddings)
    retriever = vectordb.as_retriever(
        search_type="mmr", 
        search_kwargs={"k": 8},
    )
    retriever_tool = create_retriever_tool(
        retriever,
        "search_code",
        "Searches for code related to a given command.",
    )

    return [retriever_tool, write_code]


def process_command(command: str, root_dir: str, tool_strategy: Literal['FileSystem', 'Retriever'] = 'FileSystem'):
    tools: None
    search_tool = ""
    write_tool = ""

    if tool_strategy == 'FileSystem':
        tools = FileManagementToolkit(
            root_dir=root_dir,
            selected_tools=["read_file", "write_file", "list_directory"],
        ).get_tools()
        search_tool = "'list_directory', 'read_file'"
        write_tool = "'write_file', automatically, without asking for confirmation."
    elif tool_strategy == 'Retriever':
        tools = create_retriever_strategy_tool(command, root_dir)
        search_tool = "'search_code'"
        write_tool = "'write_code', by only providing the new code."
    else:
        raise ValueError("Invalid tool strategy")

    template = f"You are an AI code generator that uses the {search_tool} function/s to retrieve the relevant files and updates code with the function {write_tool}."

    llm = ChatOpenAI(model_name=MODEL, temperature=0.7)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            ("human", "{input}"),
        ]
    )
    prompt.append(MessagesPlaceholder(variable_name="agent_scratchpad"))
    prompt.input_variables.append("agent_scratchpad")

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    response = agent_executor.invoke({"input": command})

    print(response)

def main():
    parser = argparse.ArgumentParser(prog="CodeAssistant")
    parser.add_argument("cmd", help="Command specifying which code to generate and where to write it.", type=str)
    parser.add_argument("-d", "--dir", help="Directory where the files referred in the command are located.", required=False, default="/", type=str)
    parser.add_argument("-t", "--tool", help="The Langchain toolset to use in the agent.", required=False, choices=["FileSystem","Retriever"], default="FileSystem", type=str)
    args = parser.parse_args()
   
    process_command(args.cmd, args.dir, args.tool)

if __name__ == "__main__":
    main()
