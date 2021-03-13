

## Goal
Build a simple search on IMDB top 1000. 

Given query text, return a list out movie titles which includes the query text.

## Assumptions:
1. User can search different aspects of the movie which includes:
    1. Movie name (title)
    2. Director
    3. Cast (Actor name & Charactor name)
    4. Genre
    5. Year

2. search and exact search
    1. search: treat each work in the query text seperately. 
    2. exact search: search "<exact query text>" together.
        1. only support 2 gram and 3 gram currently.
    3. The result should be the intersection of all tokens.

## High level Architecture

Crawler -> Index Builder -> Server


## Details
### Data Model and Storage
#### Storage
Option 1 Store in local files
Pros:
- More need to set up other environments.

Cons:
- Read and write speed is a bottleneck.

Option 2 Use a database
Pros:
- Database has powerful features and optimization for read and write.
- More scalable.
Cons:
- Introduce more dependencies. Our data size is relatively small.


This usercase only touch 1000 movies, I think this is a relatively small data size. Storing in files can be acceptable. Considering the convenience of less environment dependecy. Prefer to store data in local files.
It can be updated to use database in the future.

#### Data Model
Movie
- movie_id (pk)
- movie_detials

movie_details can be html page info or formatted data. Html page info contains lots of redundant data. I prefer to store formatted data.

Index
- tokens
- movie_id
- movie_title


### Crawler

Option 1: Synchronized crawling

Pros:
- Gurantee the data accuracy.

Cons:
- Slow

Option 2: Asynchronous crawling.

Pros: 
- Faster processing

Option 3: Multithread
Pros: 
- Improve the processing speed ot next level.

Prefer to use asynchronous crawling for faster processing. Can update to multithread later.

### Index Builder
The intuitive is to build a reversed index from token to movie_id.


#### Tokenization
Option 1: Simply implement by string split
Pros:
- Simple
- Not library dependency.
Cons:
- Do not handle stoping words.

Option 2: Use known library
Pros:
- More convenient and powerful. e.g. can handle stoping words
Cons:
- Introduce more dependencies.

For beta version, option 1 is enough to meet the minimum requirment.


#### 2 gram and 3 gram 
For exact search, processing 2 gram and 3 gram tokens.


### Server

#### Api Design
[list of movie titles] search_movies(query_text)

query_text: string which can contains "" for exact search.


### User Guide

#### Requirements
Please run `pip install -r requirements.txt`

#### How to ues it
Before run:
- Go to the directory of search_imdb/search_imdb.
- Create data folder. e.g. Run `mkdir data` in terminal under search_imdb/search_imdb directory.

1. Run in command line
    - Open Terminal.
    - Go to the directory of search_imdb/search_imdb.
    - Type `python3 server.py`. First time run will take some time to get data and initilize.
    - Follow the instructions in the Terminal.

2. Using API
Example file: test_api.py
    - Import the server model in search_imdb package to your py file
    - Init a MovieSearch object. e.g. `movie_search = server.MovieSearch()`
    - Call search_movies(query_text) function to get results.

### What can be improve & What's more

1. Support each of keywords in Summary.
2. Handling stopping words.
3. To handle larger size of data, we can use database, or build shards etc.
4. Stream IO.