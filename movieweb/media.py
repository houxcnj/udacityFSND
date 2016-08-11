
class Movie():
    """
        Moive class.
        Attributes: movie title, art box image and trailer yourube url
    """
    def __init__(self, movie_title, poster_image, trailer_youtube):
        """
        :param movie_title: a movie's title
        :param poster_image: the url of the art box image
        :param trailer_youtube:  the url of the movie trailer
        the initiation function
        """
        self.title = movie_title
        self.poster_image_url = poster_image
        self.trailer_youtube_url = trailer_youtube