from gql import Client, gql
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport

transport = AIOHTTPTransport(url='https://auth.chat.arnor.dev/graphql')


def login(email: str, password: str):
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql(
        """
        mutation login {
            login(email: "giga@lul.com", password: "12346") {
                jwt
            }
        }
        """
    )
    result = client.execute(query)
    print(result)
