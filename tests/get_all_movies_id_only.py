from concurrent.futures import wait
from requests_futures.sessions import FuturesSession
import time
import grpc
import movie_pb2
import movie_pb2_grpc

def test_graphql(n: int):
    print(f'Running {n} GraphQL tests')
    query = """query { all_movies { id } }"""
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
        futures = (
            session.get(f'http://movie_rest:3200/movies') for _ in range(n))
        map(lambda f: [m['id'] for m in f.result()],
            list(map(lambda f: f.result(), futures)))
        end = time.time()
    print(f'Total time to {n} tests: {end - start}s')
    return end - start

def test_grpc(n: int):
    print(f'Running {n} gRPC tests')
    with grpc.insecure_channel('movie_grpc:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)
        start = time.time()
        # initiate all requests
        futures = (stub.GetListMovies(movie_pb2.Empty()) for _ in range(n))
        list(map(lambda f: [m.id for m in f], futures))
        end = time.time()
    print(f'Total time to {n} tests: {end - start}s')
    return end - start


def run_tests():
    n_tests = 110
    return [
        test_rest(n_tests),
        test_grpc(n_tests),
        test_graphql(n_tests),
    ]


if __name__ == '__main__':
    run_tests()
