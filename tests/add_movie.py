from concurrent.futures import wait
from requests_futures.sessions import FuturesSession
import time
import grpc
import movie_pb2
import movie_pb2_grpc

Movie_id = '40cd74d7-fgre-sfgd-dfes-34235dsfef7a'

def test_graphql(n: int):
    print(f'Running {n} GraphQL tests')
    query = """mutation {{
    create_movie(_id:"{movieid}",
                 _title: "Avengers",
                 _director: "brothers russo",
                 _rate: 8.8) {{ ... on Movie {{
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

def test_grpc(n: int):
    print(f'Running {n} gRPC tests')
    with grpc.insecure_channel('movie_grpc:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)
        movie = movie_pb2.MovieData(id=Movie_id,
                                    title="Avengers",
                                    rating=8.8,
                                    director="brothers russo")
        start = time.time()
        # initiate all requests
        futures = (stub.CreateMovie.future(movie) for _ in range(n))
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total time to {n} tests: {end - start}s')
    return end - start

def test_rest(n: int):
    print(f'Running {n} REST tests')
    jsonRequest = {
        "title": "Avengers",
        "rating": 8.8,
        "director": "brothers russo"
    }
    with FuturesSession() as session:
        start = time.time()
        # initiate all requests
        futures = (session.post(f'http://movie_rest:3200/movies/{Movie_id}',
                                json=jsonRequest) for _ in range(n))
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
