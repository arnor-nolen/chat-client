from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from helper import load_query, GraphQL
from settings import settings


def login(email: str, password: str):
    transport = RequestsHTTPTransport(url=settings.auth_url)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    with client as session:
        query = load_query(GraphQL.LOGIN)
        params = {'email': email, 'password': password}
        result = session.execute(query, variable_values=params)
        return result['login']['jwt']
