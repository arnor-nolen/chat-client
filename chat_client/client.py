from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport
from settings import settings
from helper import load_query, GraphQL
from auth import login
import jwt


class Client:
    def __init__(self, email: str, password: str) -> None:
        self.token = login(email=email, password=password)
        jwt_claims = jwt.decode(
            self.token, options={"verify_signature": False}
        )
        self.user_id = int(jwt_claims['hasura']['x-hasura-user-id'])
        self.email = jwt_claims['email']
        transport = RequestsHTTPTransport(
            url=settings.data_url,
            headers={'Authorization': f'Bearer {self.token}'},
        )
        self.client = GQLClient(
            transport=transport, fetch_schema_from_transport=True
        )

    def get_all_channels(self) -> list[dict]:
        return self.dispatch_request(GraphQL.GET_ALL_CHANNELS)['Channel']

    def dispatch_request(self, query: GraphQL, params: dict = {}) -> dict:
        return self.client.execute(load_query(query), variable_values=params)

    def get_my_channels(self) -> list[dict]:
        result = self.dispatch_request(
            GraphQL.GET_MY_CHANNELS, params={'user_id': self.user_id}
        )['UsersOnChannels']
        return [x['Channel'] for x in result]

    def get_messages(self, channel_id: int) -> list[dict]:
        result = self.dispatch_request(
            GraphQL.GET_MESSAGES, params={'channel_id': channel_id}
        )['Message']
        return result

    def send_message(self, channel_id: int, text: str) -> int:
        result = self.dispatch_request(
            GraphQL.SEND_MESSAGE,
            params={
                'user_id': self.user_id,
                'channel_id': channel_id,
                'text': text,
            },
        )['insert_Message_one']['id']
        return result
