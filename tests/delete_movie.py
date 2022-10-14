from concurrent.futures import wait
from requests_futures.sessions import FuturesSession
import time
import grpc
import movie_pb2
import movie_pb2_grpc

Movie_id = '276c79ec-a26a-40a6-b3d3-fb242a5947b6'

def test_graphql(n: int):
    print(f'Running {n} GraphQL tests')
    query = """mutation {{ delete_movie(_id:"{movieid}") {{ ... on Movie {{
        title
        rating
        director
        id }} }} }}""".format(movieid=Movie_id)
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
        futures = (session.delete(f'http://movie_rest:3200/movies/{Movie_id}')
                   for _ in range(n))
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total time to {n} tests: {end - start}s')
    return end - start

def test_grpc(n: int):
    print(f'Running {n} gRPC tests')
    with grpc.insecure_channel('movie_grpc:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)
        movieid = movie_pb2.MovieID(id=Movie_id)
        start = time.time()
        # initiate all requests
        futures = (stub.RemoveMovie.future(movieid) for _ in range(n))
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total time to {n} tests: {end - start}s')
    return end - start

def run_tests():
    n_tests = 110.
    rest = test_rest(n_tests)
    grpc = test_grpc(n_tests)
    graphql = test_graphql(n_tests)
    data = [rest, grpc, graphql]
    return data


if __name__ == '__main__':
    run_tests()
