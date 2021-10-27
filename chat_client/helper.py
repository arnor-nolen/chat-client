import glob
import re
from gql import gql
from graphql.language.ast import DocumentNode
from enum import Enum


def get_query_name(file_name: str):
    regexp = re.compile('([^/]*)\.graphql', re.IGNORECASE)
    if match := re.search(regexp, file_name):
        return match.group(1)


file_names = glob.glob('./chat_client/graphql/*.graphql')
enum_names = [get_query_name(x) for x in file_names]
GraphQL = Enum('GraphQL', {x.upper(): x for x in enum_names})
"""
Enum of all available GraphQL queries, constructed from files
in `./chat_client/graphql/` folder
"""


def load_query(query: GraphQL) -> DocumentNode:
    with open(f'./chat_client/graphql/{query.value}.graphql', 'r') as file:
        data = file.read()
    return gql(data)
