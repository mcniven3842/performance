from concurrent.futures import wait
from requests_futures.sessions import FuturesSession
import time
import grpc
import movie_pb2
import movie_pb2_grpc

Movie_id = '39ab85e5-5e8e-4dc5-afea-65dc368bd7ab'

def test_graphql(n: int):
    print(f'Running {n} GraphQL tests')
    query = """query {{ movie_with_id(_id: "{movieid}") {{ ... on Movie {{
        id
        title
        rating
        director
    }} }} }}""".format(movieid=Movie_id)
    with FuturesSession() as session:
        start = time.time()
        # initiate all requests
        futures = (session.post('http://movie_graphql:3301/graphql',
                                json={'query': query}) for _ in range(n))
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total time to {n} tests: {end - start}s')
    return end - start

def test_rest(n: int):
    print(f'Running {n} REST tests')
    with FuturesSession() as session:
        start = time.time()
        # initiate all requests
        futures = (session.get(f'http://movie_rest:3200/movies/{Movie_id}')
                   for _ in range(n))
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total time to {n} tests: {end - start}s')
    return end - start


def run_tests():
    n_tests = 110
    rest = test_rest(n_tests)
    grpc = test_grpc(n_tests)
    graphql = test_graphql(n_tests)
    data = [rest, grpc, graphql]
    return data


if __name__ == '__main__':
    run_tests()
