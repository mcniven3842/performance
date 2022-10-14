import grpc
from concurrent import futures
import movie_pb2
import movie_pb2_grpc
import json
from google.protobuf.json_format import MessageToJson

EMPTY_MOVIE_DATA = movie_pb2.MovieData(title="",
                                       rating=float("nan"),
                                       director="",
                                       id="")


class MovieServicer(movie_pb2_grpc.MovieServicer):

    def __init__(self):
        with open('{}/data/movies.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["movies"]

    def GetMovieByID(self, request, context):
        print('Request received for GetMovieByID')
        print(f'Request message:\n{request}')

        for movie in self.db:
            if movie['id'] == request.id:
                print("Movie found!")
                return movie_pb2.MovieData(title=movie['title'],
                                           rating=float(movie['rating']),
                                           director=movie['director'],
                                           id=movie['id'])
        print("Movie NOT found!")
        return EMPTY_MOVIE_DATA

    def GetMoviesFiltered(self, request, context):
        print('Request received for GetMoviesFiltered')
        print(f'Request message:\n{request}')

        rating = request.rating
        for movie in self.db:
            if float(movie['rating']) >= rating:
                print(f'Yielding movie {movie}')
                yield movie_pb2.MovieData(**movie)

    def GetListMovies(self, request, context):
        print('Request received for GetListMovies')
        print(f'Request message:\n{request}')

        for movie in self.db:
            print(f'Yielding movie {movie}')
            yield movie_pb2.MovieData(title=movie['title'],
                                      rating=float(movie['rating']),
                                      director=movie['director'],
                                      id=movie['id'])

    def GetMovieByTitle(self, request, context):
        print('Request received for GetMovieByTitle')
        print(f'Request message:\n{request}')

        for movie in self.db:
            if movie['title'] == request.title:
                print("Movie found!")
                return movie_pb2.MovieData(title=movie['title'],
                                           rating=float(movie['rating']),
                                           director=movie['director'],
                                           id=movie['id'])
        print("Movie NOT found!")
        return EMPTY_MOVIE_DATA

    def CreateMovie(self, request, context):
        print('Request received for CreateMovie')
        print(f'Request message:\n{request}')

        # NOTE: not checking existance of movie for testing purposes
        # for movie in self.db:
        #     if str(movie['id']) == str(request.id):
        #         print("Movie already exists!")
        #         return movie_pb2.FeedbackMessage(
        #             message='movie ID already exists', movie=EMPTY_MOVIE_DATA)

        movie_json = json.loads(MessageToJson(request))
        self.db.append(movie_json)
        print("Movie added!")
        return movie_pb2.FeedbackMessage(
            message='movie added', movie=movie_pb2.MovieData(**movie_json))

    def UpdateMovieRating(self, request, context):
        print('Request received for UpdateMovieRating')
        print(f'Request message:\n{request}')

        # check if oneOf field is present
        if request.id:
            field, ref = 'id', request.id
        elif request.title:
            field, ref = 'title', request.title
        else:
            print("Missing parameters!")
            return movie_pb2.FeedbackMessage(
                message='needs at least one of id or title',
                movie=EMPTY_MOVIE_DATA)

        # find movie and update it
        for movie in self.db:
            if str(movie[field]) == str(ref):
                movie['rating'] = float(request.rating)
                print('Movie rating updated!')
                return movie_pb2.FeedbackMessage(
                    message='movie rating updated',
                    movie=movie_pb2.MovieData(**movie))

        print("Movie NOT found!")
        return movie_pb2.FeedbackMessage(message='movie not found',
                                         movie=EMPTY_MOVIE_DATA)

    def RemoveMovie(self, request, context):
        print('Request received for RemoveMovie')
        print(f'Request message:\n{request}')

        for movie in self.db:
            if str(movie['id']) == str(request.id):
                self.db.remove(movie)
                print("Movie removed!")
                return movie_pb2.FeedbackMessage(
                    message='movie removed', movie=movie_pb2.MovieData(**movie))

        print("Movie NOT found!")
        return movie_pb2.FeedbackMessage(message='movie not found',
                                         movie=EMPTY_MOVIE_DATA)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_MovieServicer_to_server(MovieServicer(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    print('gRPC Server running on port 3001')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
