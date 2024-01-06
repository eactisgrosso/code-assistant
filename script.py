import argparse
import os
# import re
# from langchain_community.document_loaders.generic import GenericLoader
# from langchain_community.document_loaders.parsers import LanguageParser
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import DocArrayInMemorySearch
# from langchain.tools.retriever import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.agent_toolkits import FileManagementToolkit

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MODEL = os.environ.get('MODEL', 'gpt-4-1106-preview')

# def create_retriever():
#     code = []
#     for file_path in files:
#         try:
#             loader = GenericLoader.from_filesystem(
#                 file_path,
#                 glob="*",
#                 suffixes=[".py", ".js"],
#                 parser=LanguageParser(),
#             )
#             docs = loader.load()
#             code.extend(docs) 
#         except FileNotFoundError:
#             print(f"File not found: {file_path}")


#     embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
#     vectordb = DocArrayInMemorySearch.from_documents(code, embeddings)
#     retriever = vectordb.as_retriever(
#         search_type="mmr", 
#         search_kwargs={"k": 8},
#     )
#     retriever_tool = create_retriever_tool(
#         retriever,
#         "code_search",
#         "Searches for code related to a given command.",
#     )

def process_command(command, root_dir):
    tools = FileManagementToolkit(
        root_dir=root_dir,
        selected_tools=["read_file", "write_file", "list_directory"],
    ).get_tools()

    # tools.append(retriever_tool)
    llm = ChatOpenAI(model_name=MODEL, temperature=0.7)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an AI code generator that uses the 'list_directory','read_file' and 'write_file' functions to retrieve relevant code fragments and update code in files automcatically, without asking for confirmation."),
            ("human", "{input}"),
        ]
    )
    prompt.append(MessagesPlaceholder(variable_name="agent_scratchpad"))
    prompt.input_variables.append("agent_scratchpad")

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    response = agent_executor.invoke({"input": command})

    print(response)


def find_file_paths(root_directory, file_names):
    file_paths = []

    for dirpath, dirnames, filenames in os.walk(root_directory):
        for file in filenames:
            if file in file_names:
                full_path = os.path.join(dirpath, file)
                file_paths.append(full_path)

    return file_paths


file_pattern = r'\b\w+\.\w+\b'
def main():
    parser = argparse.ArgumentParser(prog="CodeAssistant")
    parser.add_argument("cmd", help="Command specifying which code to generate and where to write it.", type=str)
    parser.add_argument("-d", "--dir", help="Directory where the files referred in the command are located.", required=False, default="/", type=str)
    args = parser.parse_args()
    command = args.cmd
    dir = args.dir

    # file_names = re.findall(file_pattern, command)
    # file_paths = find_file_paths(dir, file_names)

    # print("The following files will be used as context and/or code destination:\n", file_paths)

    process_command(command, dir)

if __name__ == "__main__":
    main()
