# import json
import webbrowser
import pickle
import spotipy
from urllib import urlopen
from bs4 import BeautifulSoup
import unittest

# def pretty(obj):
#     return json.dumps(obj, sort_keys=True, indent=2)

## building an "API mashup"

spotify_clientid = '377b1cc2780040be8baf92c82e56d67e'           #Spotify Client ID
spotify_clientsecret = 'b7081e49cc804bc494526e72cdcad67c'       #Spotify Client Secret
spotify_URI = 'spotify:track:17oLsEzzlGFlrBKViCzmGc'            #Spotify URI

artist_name = 'U2'
#artist_name = raw_input('Please type the name of the artist: ')


cache_songs = 'cached_songs.txt'
cache_artists = 'cached_artists.txt'

try:
    f = open(cache_artists,'r')
    saved_cache_artists = pickle.load(f)
    f.close()
except:
    saved_cache_artists = {}

try:
    f = open(cache_songs,'r')
    saved_cache_songs = pickle.load(f)
    f.close()
except:
    saved_cache_songs = {}


class Artist:


    def __init__(self, artist_name, search_number = 5):
        self.artist_name = artist_name
        self.search_number = search_number

    def artist_uri(self):
        if self.artist_name not in saved_cache_artists:
            results = spotipy.Spotify().search(q='artist:' + self.artist_name, type='artist')
            artist_uri = results['artists']['items'][0]['uri']

            saved_cache_artists[self.artist_name]={}
            saved_cache_artists[self.artist_name]['artist_uri'] = artist_uri
            f = open(cache_artists, 'w')
            pickle.dump(saved_cache_artists, f)
            f.close()
        elif 'artist_uri' not in saved_cache_artists[self.artist_name]:
            results = spotipy.Spotify().search(q='artist:' + self.artist_name, type='artist')
            artist_uri = results['artists']['items'][0]['uri']

            saved_cache_artists[self.artist_name]['artist_uri'] = artist_uri
            f = open(cache_artists, 'w')
            pickle.dump(saved_cache_artists, f)
            f.close()
        else:
            artist_uri = saved_cache_artists[self.artist_name]['artist_uri']
        return artist_uri

    def top_songs(self):
        if self.artist_name not in saved_cache_artists:

            q = spotipy.Spotify().artist_top_tracks(self.artist_uri())['tracks'][:self.search_number]        
            res = [i['name'].encode('utf-8') for i in q]

            saved_cache_artists[self.artist_name]={}
            saved_cache_artists[self.artist_name]['top_songs'] = res
            f = open(cache_artists, 'w')
            pickle.dump(saved_cache_artists, f)
            f.close()
        elif 'top_songs' not in saved_cache_artists[self.artist_name]:

            q = spotipy.Spotify().artist_top_tracks(self.artist_uri())['tracks'][:self.search_number]        
            res = [i['name'].encode('utf-8') for i in q]

            saved_cache_artists[self.artist_name]['top_songs'] = res
            f = open(cache_artists, 'w')
            pickle.dump(saved_cache_artists, f)
            f.close()        
        else:
            res = saved_cache_artists[self.artist_name]['top_songs']
        return res

    def top_ten_index_list(self):
        artist_songs = Artist(self.artist_name)

        song_list = list(artist_songs.top_songs())
        song_list_revised = []

        for i in song_list:
            if '-' in i:
                q = i.split('-')[0]
                song_list_revised.append(q)
            else:
                song_list_revised.append(i)

        song_performance_10_list = [Song(i).topten_performance() for i in song_list_revised if Song(i).topten_performance() != [0,0]]
        
        song_performance_10_list.sort(key = lambda x:x[0])
        return song_performance_10_list

    def top_ten_index(self):
        if len(self.top_ten_index_list()) == 0:
            return 0.0
        else:
            q = [i[0] for i in self.top_ten_index_list()]
            return sum(q)*1.0/len(q)

    def top_fifty_index_list(self):
        artist_songs = Artist(self.artist_name)

        song_list = list(artist_songs.top_songs())
        song_list_revised = []

        for i in song_list:
            if '-' in i:
                q = i.split('-')[0]
                song_list_revised.append(q)
            else:
                song_list_revised.append(i)

        song_performance_50_list = [Song(i).topfifty_performance() for i in song_list_revised if Song(i).topfifty_performance() != [0,0]]
        
        song_performance_50_list.sort(key = lambda x:x[0])
        return song_performance_50_list

    def top_fifty_index(self):
        if len(self.top_fifty_index_list()) == 0:
            return 0.0
        else:
            q = [i[0] for i in self.top_fifty_index_list()]
            return sum(q)*1.0/len(q)




class Song:

    def __init__(self, Song_name):
        self.Song_name = Song_name
        if '-' in Song_name:
            self.search_name = Song_name.split('-')[0]
        else:
            self.search_name = Song_name
        self.overall_performance = self.overall_performance()

    def score_list(self):
        if self.Song_name not in saved_cache_songs:
            soup_url = "http://en.wikipedia.org/wiki/{}".format(self.search_name)
            soup = BeautifulSoup(urlopen(soup_url),"html.parser")
            table = soup.find_all('table', class_="wikitable")
            score_list=[]
            for tag in soup.find_all('table', class_="wikitable"):
                for tag2 in tag.find_all('td'):
                    if len(tag2.contents)>0 and is_int(tag2.contents[-1]):
                        if int(unicode(tag2.contents[-1])) < 100:
                            score_list.append(int(unicode(tag2.contents[-1])))
            saved_cache_songs[self.Song_name] = score_list
            f = open(cache_songs, 'w')
            pickle.dump(saved_cache_songs, f)
            f.close()
        else:
            score_list = saved_cache_songs[self.Song_name]
        return score_list

    def overall_performance(self):
        score_list_top100 = [i for i in self.score_list() if i <= 100]
        if len(score_list_top100) > 0:
            res= [sum(score_list_top100)*1.0/len(score_list_top100), len(score_list_top100)]
        else:
            res = [0,0]
        return res


    def topten_performance(self):
        score_list_sorted = sorted(self.score_list())
        score_list_topten = [i for i in score_list_sorted if i <= 10]
        if len(score_list_topten) > 0:
            res= [sum(score_list_topten)*1.0/len(score_list_topten), len(score_list_topten)]
        else:
            res = [0,0]
        return res

    def topfifty_performance(self):
        score_list_sorted = sorted(self.score_list())
        score_list_topten = [i for i in score_list_sorted if i <= 50]
        if len(score_list_topten) > 0:
            res= [sum(score_list_topten)*1.0/len(score_list_topten), len(score_list_topten)]
        else:
            res = [0,0]
        return res

def is_int(s):
    try: 
        int(s)
        return True
    except:
        return False



endline = '----'*8+'\n'

Choice_1 = raw_input("\n\tFor the popularity index of an artist's Spotify first 5 songs, enter '1': \n\t\
For the popularity index of a specific song, enter '2'. \n")
if Choice_1 == "1":
    artist_input = raw_input(endline+"\n\tPlease enter the artist's name: \n")
    Choice_2 = raw_input(endline+"\n\tFor the artist {}, please enter the corresponding number for your result: \n\n\t\
1 - First 5 songs in Spotify \n\t2 - Chart results \n\t3 - Top 10 index \n\t4 - Top 50 index\n".format(artist_input))
    if Choice_2 == '1':
        print endline+'\nFirst 5 songs of {} in Spotify are:\n'.format(artist_input)
        for i in Artist(artist_input).top_songs():
            print '\t'+i
        print '\n'+endline
    elif Choice_2 == '2':
        print endline
        for i in Artist(artist_input).top_songs():
            song = Song(i)
            rank = song.overall_performance
            if rank == [0,0]:
                print "The song '{}' did not ranked within 100th on any chart".format(song.Song_name)       
            else:
                print "The song '{}' ranked {} on average over {} charts.".format(song.Song_name, rank[0], rank[1])
        print endline
    elif Choice_2 == '3':
        print endline + "The Top 10 index of {} is: {}. ({})".format(artist_input, Artist(artist_input).top_ten_index(),Artist(artist_input).top_ten_index_list())
        print endline
    elif Choice_2 == '4':
        print endline + "The Top 50 index of {} is: {}. ({})".format(artist_input, Artist(artist_input).top_fifty_index(),Artist(artist_input).top_fifty_index_list())
        print endline
    else:
        print 'Invalid'

elif Choice_1 == "2":
    song = Song(raw_input("Please enter the song's name: \n"))
    rank = song.overall_performance
    print endline
    if rank == [0,0]:
        print "The song '{}' did not ranked within 100th on any chart".format(song.Song_name)       
    else:
        print "The song '{}' ranked {} on average on {} charts.".format(song.Song_name, rank[0], rank[1])   

else:
    print 'Invalid'


#-------------------------------------Unit Tests-------------------------------------------

class test1(unittest.TestCase):
    def test_top_ten_index_list(self):
        if Choice_1 == '1':
            self.assertEqual(type(Artist(artist_input).top_ten_index_list()), type([]))


class test2(unittest.TestCase):
    def test_top_fifty_index_list(self):
        if Choice_1 == '1':
            self.assertEqual(type(Artist(artist_input).top_fifty_index_list()), type([]))

class test3(unittest.TestCase):
    def test_top_ten_index(self):
        if Choice_1 == '1':
            self.assertEqual(type(Artist(artist_input).top_ten_index()), type(1.0))

class test4(unittest.TestCase):
    def test_top_fifty_index(self):
        if Choice_1 == '1':
            self.assertEqual(type(Artist(artist_input).top_fifty_index()), type(1.0))

class test5(unittest.TestCase):
    def test_score_list(self):
        if Choice_1 == '2':
            self.assertEqual(type(song.score_list()), type([]))

class test6(unittest.TestCase):
    def test_top_ten_performance(self):
        if Choice_1 == '2':
            self.assertEqual(type(song.topten_performance()), type([]))
            self.assertEqual(len(song.topten_performance()), 2)

class test7(unittest.TestCase):
    def test_top_fifty_performance(self):
        if Choice_1 == '2':
            self.assertEqual(type(song.topfifty_performance()), type([]))
            self.assertEqual(len(song.topfifty_performance()), 2)

class test9(unittest.TestCase):
    def test_overall_performance(self):
        if Choice_1 == '2':
            self.assertEqual(type(song.overall_performance), type([]))
            self.assertEqual(len(song.overall_performance), 2)

unittest.main(verbosity=2)
