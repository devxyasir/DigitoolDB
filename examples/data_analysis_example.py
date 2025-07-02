#!/usr/bin/env python3
"""
Data Analysis Example with DigitoolDB

This example demonstrates how to:
1. Import external data into DigitoolDB
2. Query and analyze the data
3. Perform aggregation-like operations
4. Create reports based on the analysis

The example uses a movie dataset to demonstrate real-world data handling.
"""
import sys
import time
import json
import csv
from pathlib import Path
from datetime import datetime
import os

# Add the parent directory to the Python path to import the DigitoolDB modules
sys.path.append(str(Path(__file__).parent.parent))

from src.client.simple_api import SimpleDB
from src.server.server import DigitoolDBServer


# Sample movie data (normally you would load this from a CSV/JSON file)
SAMPLE_MOVIES = [
    {"title": "The Shawshank Redemption", "year": 1994, "rating": 9.3, "director": "Frank Darabont", 
     "genre": ["Drama"], "runtime": 142},
    {"title": "The Godfather", "year": 1972, "rating": 9.2, "director": "Francis Ford Coppola", 
     "genre": ["Crime", "Drama"], "runtime": 175},
    {"title": "The Dark Knight", "year": 2008, "rating": 9.0, "director": "Christopher Nolan", 
     "genre": ["Action", "Crime", "Drama"], "runtime": 152},
    {"title": "Pulp Fiction", "year": 1994, "rating": 8.9, "director": "Quentin Tarantino", 
     "genre": ["Crime", "Drama"], "runtime": 154},
    {"title": "Fight Club", "year": 1999, "rating": 8.8, "director": "David Fincher", 
     "genre": ["Drama"], "runtime": 139},
    {"title": "Inception", "year": 2010, "rating": 8.8, "director": "Christopher Nolan", 
     "genre": ["Action", "Adventure", "Sci-Fi"], "runtime": 148},
    {"title": "The Matrix", "year": 1999, "rating": 8.7, "director": "Lana Wachowski", 
     "genre": ["Action", "Sci-Fi"], "runtime": 136},
    {"title": "Goodfellas", "year": 1990, "rating": 8.7, "director": "Martin Scorsese", 
     "genre": ["Biography", "Crime", "Drama"], "runtime": 146},
    {"title": "The Silence of the Lambs", "year": 1991, "rating": 8.6, "director": "Jonathan Demme", 
     "genre": ["Crime", "Drama", "Thriller"], "runtime": 118},
    {"title": "Interstellar", "year": 2014, "rating": 8.6, "director": "Christopher Nolan", 
     "genre": ["Adventure", "Drama", "Sci-Fi"], "runtime": 169},
    {"title": "The Lord of the Rings: The Fellowship of the Ring", "year": 2001, "rating": 8.8, 
     "director": "Peter Jackson", "genre": ["Adventure", "Drama", "Fantasy"], "runtime": 178},
    {"title": "Forrest Gump", "year": 1994, "rating": 8.8, "director": "Robert Zemeckis", 
     "genre": ["Drama", "Romance"], "runtime": 142},
    {"title": "The Lion King", "year": 1994, "rating": 8.5, "director": "Roger Allers", 
     "genre": ["Animation", "Adventure", "Drama"], "runtime": 88},
    {"title": "Gladiator", "year": 2000, "rating": 8.5, "director": "Ridley Scott", 
     "genre": ["Action", "Adventure", "Drama"], "runtime": 155},
    {"title": "Titanic", "year": 1997, "rating": 7.8, "director": "James Cameron", 
     "genre": ["Drama", "Romance"], "runtime": 194},
]


class MovieAnalyzer:
    """Movie dataset analyzer using DigitoolDB"""
    
    def __init__(self):
        """Initialize the movie analyzer"""
        # Connect to the database
        self.db = SimpleDB()
        self.db.connect()
        
        # Set up database and collections
        if "movie_analysis" not in self.db.list_dbs():
            self.db.create_db("movie_analysis")
        
        self.movie_db = self.db.db("movie_analysis")
        
        # Create collections if they don't exist
        if "movies" not in self.movie_db.list_collections():
            self.movie_db.create_collection("movies")
            
            # Create indices for better query performance
            movies = self.movie_db.collection("movies")
            movies.create_index("year")
            movies.create_index("rating")
            movies.create_index("director")
            print("Created movies collection with indices")
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'db') and self.db.connected:
            self.db.disconnect()
    
    def import_sample_data(self):
        """Import sample movie data into the database"""
        movies = self.movie_db.collection("movies")
        
        # Check if we already have data
        existing = movies.find()
        if existing:
            print(f"Found {len(existing)} existing movies. Skipping import.")
            return
        
        # Import the sample data
        movie_ids = []
        for movie in SAMPLE_MOVIES:
            # Add import timestamp
            movie["imported_at"] = datetime.now().isoformat()
            movie_id = movies.insert(movie)
            movie_ids.append(movie_id)
        
        print(f"Imported {len(movie_ids)} movies into the database")
        return movie_ids
    
    def import_from_csv(self, csv_path):
        """
        Import movie data from a CSV file
        
        The CSV should have headers matching the movie schema.
        
        Args:
            csv_path (str): Path to the CSV file
            
        Returns:
            list: IDs of the imported movies
        """
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return []
        
        movies = self.movie_db.collection("movies")
        movie_ids = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert string values to appropriate types
                if 'year' in row:
                    row['year'] = int(row['year'])
                if 'rating' in row:
                    row['rating'] = float(row['rating'])
                if 'runtime' in row:
                    row['runtime'] = int(row['runtime'])
                if 'genre' in row and isinstance(row['genre'], str):
                    # Assume genre is comma-separated in the CSV
                    row['genre'] = [g.strip() for g in row['genre'].split(',')]
                
                # Add import timestamp
                row["imported_at"] = datetime.now().isoformat()
                
                # Insert into database
                movie_id = movies.insert(row)
                movie_ids.append(movie_id)
        
        print(f"Imported {len(movie_ids)} movies from {csv_path}")
        return movie_ids
    
    def get_movies_by_year(self, year):
        """
        Get all movies from a specific year
        
        Args:
            year (int): Year to filter by
            
        Returns:
            list: Movies from the specified year
        """
        movies = self.movie_db.collection("movies")
        results = movies.find({"year": year})
        
        print(f"Movies from {year}:")
        for movie in results:
            print(f"- {movie['title']} (Rating: {movie['rating']})")
        
        return results
    
    def get_movies_by_director(self, director):
        """
        Get all movies by a specific director
        
        Args:
            director (str): Director name
            
        Returns:
            list: Movies by the specified director
        """
        movies = self.movie_db.collection("movies")
        results = movies.find({"director": director})
        
        print(f"Movies directed by {director}:")
        for movie in results:
            print(f"- {movie['title']} ({movie['year']}, Rating: {movie['rating']})")
        
        return results
    
    def get_top_rated_movies(self, limit=5):
        """
        Get the top rated movies
        
        Args:
            limit (int): Number of movies to return
            
        Returns:
            list: Top rated movies
        """
        movies = self.movie_db.collection("movies")
        all_movies = movies.find()
        
        # Sort by rating (descending)
        sorted_movies = sorted(all_movies, key=lambda x: x.get('rating', 0), reverse=True)
        top_movies = sorted_movies[:limit]
        
        print(f"Top {limit} rated movies:")
        for i, movie in enumerate(top_movies, 1):
            print(f"{i}. {movie['title']} ({movie['year']}) - Rating: {movie['rating']}")
        
        return top_movies
    
    def get_movies_by_genre(self, genre):
        """
        Get movies in a specific genre
        
        Args:
            genre (str): Genre to filter by
            
        Returns:
            list: Movies in the specified genre
        """
        movies = self.movie_db.collection("movies")
        all_movies = movies.find()
        
        # Filter by genre (we need to check if genre is in the list)
        genre_movies = [m for m in all_movies if genre in m.get('genre', [])]
        
        print(f"Movies in the {genre} genre:")
        for movie in genre_movies:
            print(f"- {movie['title']} ({movie['year']}, Rating: {movie['rating']})")
        
        return genre_movies
    
    def get_average_rating_by_year(self):
        """
        Calculate the average rating for movies by year
        
        Returns:
            dict: Year to average rating mapping
        """
        movies = self.movie_db.collection("movies")
        all_movies = movies.find()
        
        # Group movies by year
        movies_by_year = {}
        for movie in all_movies:
            year = movie.get('year')
            if year not in movies_by_year:
                movies_by_year[year] = []
            movies_by_year[year].append(movie)
        
        # Calculate average rating by year
        avg_by_year = {}
        for year, year_movies in movies_by_year.items():
            total_rating = sum(m.get('rating', 0) for m in year_movies)
            avg_rating = total_rating / len(year_movies)
            avg_by_year[year] = round(avg_rating, 2)
        
        # Display results
        print("Average movie rating by year:")
        for year in sorted(avg_by_year.keys()):
            print(f"{year}: {avg_by_year[year]}")
        
        return avg_by_year
    
    def get_movies_by_runtime(self, min_runtime=None, max_runtime=None):
        """
        Get movies filtered by runtime
        
        Args:
            min_runtime (int, optional): Minimum runtime in minutes
            max_runtime (int, optional): Maximum runtime in minutes
            
        Returns:
            list: Movies matching the runtime criteria
        """
        movies = self.movie_db.collection("movies")
        all_movies = movies.find()
        
        # Filter by runtime
        filtered_movies = all_movies
        if min_runtime is not None:
            filtered_movies = [m for m in filtered_movies if m.get('runtime', 0) >= min_runtime]
        if max_runtime is not None:
            filtered_movies = [m for m in filtered_movies if m.get('runtime', 0) <= max_runtime]
        
        # Display results
        runtime_desc = ""
        if min_runtime is not None and max_runtime is not None:
            runtime_desc = f"between {min_runtime} and {max_runtime} minutes"
        elif min_runtime is not None:
            runtime_desc = f"longer than {min_runtime} minutes"
        elif max_runtime is not None:
            runtime_desc = f"shorter than {max_runtime} minutes"
        
        print(f"Movies with runtime {runtime_desc}:")
        for movie in filtered_movies:
            print(f"- {movie['title']} ({movie['runtime']} minutes)")
        
        return filtered_movies
    
    def generate_report(self, output_file="movie_report.json"):
        """
        Generate a comprehensive report of the movie database
        
        Args:
            output_file (str): Path to save the report
            
        Returns:
            dict: The generated report data
        """
        movies = self.movie_db.collection("movies")
        all_movies = movies.find()
        
        # Basic stats
        total_movies = len(all_movies)
        avg_rating = sum(m.get('rating', 0) for m in all_movies) / total_movies if total_movies > 0 else 0
        avg_runtime = sum(m.get('runtime', 0) for m in all_movies) / total_movies if total_movies > 0 else 0
        
        # Find all years
        years = sorted(set(m.get('year') for m in all_movies))
        
        # Find all directors
        directors = set(m.get('director') for m in all_movies)
        
        # Find all genres
        all_genres = set()
        for movie in all_movies:
            for genre in movie.get('genre', []):
                all_genres.add(genre)
        
        # Count movies by director
        movies_by_director = {}
        for director in directors:
            director_movies = [m for m in all_movies if m.get('director') == director]
            movies_by_director[director] = len(director_movies)
        
        # Count movies by genre
        movies_by_genre = {}
        for genre in all_genres:
            genre_movies = [m for m in all_movies if genre in m.get('genre', [])]
            movies_by_genre[genre] = len(genre_movies)
        
        # Build report
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_movies": total_movies,
            "average_rating": round(avg_rating, 2),
            "average_runtime": round(avg_runtime, 2),
            "year_range": [min(years), max(years)] if years else [],
            "total_directors": len(directors),
            "total_genres": len(all_genres),
            "movies_by_director": dict(sorted(movies_by_director.items(), key=lambda x: x[1], reverse=True)),
            "movies_by_genre": dict(sorted(movies_by_genre.items(), key=lambda x: x[1], reverse=True)),
            "top_rated_movies": [
                {"title": m["title"], "year": m["year"], "rating": m["rating"]}
                for m in self.get_top_rated_movies(5)
            ]
        }
        
        # Save report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nMovie Database Report:")
        print(f"Total Movies: {report['total_movies']}")
        print(f"Average Rating: {report['average_rating']}")
        print(f"Average Runtime: {report['average_runtime']} minutes")
        print(f"Year Range: {report['year_range'][0]} to {report['year_range'][1]}")
        print(f"Number of Directors: {report['total_directors']}")
        print(f"Number of Genres: {report['total_genres']}")
        
        print("\nTop 3 Directors by Number of Movies:")
        for director, count in list(report["movies_by_director"].items())[:3]:
            print(f"- {director}: {count} movies")
        
        print("\nTop 3 Genres by Number of Movies:")
        for genre, count in list(report["movies_by_genre"].items())[:3]:
            print(f"- {genre}: {count} movies")
        
        print(f"\nReport saved to {output_file}")
        
        return report


def main():
    """Main example function"""
    print("DigitoolDB Movie Analysis Example")
    print("================================")
    
    # Start server in background
    print("\nStarting DigitoolDB server...")
    server = DigitoolDBServer()
    
    import threading
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(1)
    
    # Create and run the Movie Analyzer
    try:
        analyzer = MovieAnalyzer()
        
        # Import sample data
        print("\nImporting sample movie data...")
        analyzer.import_sample_data()
        
        # Perform various analyses
        print("\n1. Finding movies from 1994:")
        analyzer.get_movies_by_year(1994)
        
        print("\n2. Finding movies by Christopher Nolan:")
        analyzer.get_movies_by_director("Christopher Nolan")
        
        print("\n3. Top 5 rated movies:")
        analyzer.get_top_rated_movies(5)
        
        print("\n4. Movies in the Drama genre:")
        analyzer.get_movies_by_genre("Drama")
        
        print("\n5. Average rating by year:")
        analyzer.get_average_rating_by_year()
        
        print("\n6. Movies with runtime between 150 and 180 minutes:")
        analyzer.get_movies_by_runtime(min_runtime=150, max_runtime=180)
        
        print("\n7. Generating comprehensive report:")
        analyzer.generate_report("movie_report.json")
        
        # Clean up - in a real app, you might want to keep the data
        print("\nCleaning up...")
        # Uncomment to clean up:
        # analyzer.db.drop_db("movie_analysis")
        
    finally:
        # Stop the server
        print("\nStopping server...")
        server.stop()
    
    print("\nExample completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
