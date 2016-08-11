import media    # import module media
import fresh_tomatoes # import module fresh_tomatoes

# initiate 5 movie objects
forrest_gump = media.Movie("Forrest Gump",
                           "https://upload.wikimedia.org/wikipedia/en/6/67/Forrest_Gump_poster.jpg",
                           "https://www.youtube.com/watch?v=bLvqoHBptjg")
clockwork = media.Movie("A Clockwork Orange",
                        "https://upload.wikimedia.org/wikipedia/en/4/48/Clockwork_orangeA.jpg",
                        "https://www.youtube.com/watch?v=SPRzm8ibDQ8")
darkknight = media.Movie("The Dark Knight",
                         "https://upload.wikimedia.org/wikipedia/en/8/8a/Dark_Knight.jpg",
                         "https://www.youtube.com/watch?v=EXeTwQWrcwY")
furious = media.Movie("Furious 7",
                      "https://upload.wikimedia.org/wikipedia/en/b/b8/Furious_7_poster.jpg",
                      "https://www.youtube.com/watch?v=yISKeT6sDOg")
spiderman = media.Movie("Spider man",
                        "https://upload.wikimedia.org/wikipedia/en/f/f3/Spider-Man2002Poster.jpg",
                        "https://www.youtube.com/watch?v=O7zvehDxttM")

# store it to a list called movies
movies = [forrest_gump, clockwork, darkknight, furious, spiderman]

# call the function in fresh_tomatoes.py
fresh_tomatoes.open_movies_page(movies)