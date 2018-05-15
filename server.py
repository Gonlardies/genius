import requests, json
from time import sleep
import http.client
import http.server
import socketserver
import json

PORT = 8000
API_URL = "https://api.genius.com"
CLIENT_ACCESS_TOKEN = "8kCYQlH5MmRgxPDXW4VIif5uth6PCwQGbT383fHxlULsuJ79hhA6dxmz4gs7FT1M"


class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    LIST = []
    def main_page(self):
        HTML = """
            <html>
                <head>
                    <title>Genius</title>
                </head>
                <body align=center>
                    <h1>Bienvenido a Genius</h1>
                    <h2><u>Buscar artista</u></h2>
                    <form method="get" action="searchSongs">
                        <input type = "text" name="artist"></input><br>
                        <p><input type = "submit">
                        </input>
                    </form>
                </body>
            </html>
                """
        return HTML
    def send_headers(self):
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):

        if self.path == '/':
            self.send_response(200)
            self.send_headers()
            page = self.main_page()
            self.wfile.write(bytes(page, "utf8"))
        elif 'searchSongs' in self.path:
            self.LIST.clear()
            self.send_response(200)
            self.send_headers()
            self.ARTIST_NAME = self.path.split('?')[1].split('=')[1]
            if '+' in self.ARTIST_NAME:
                self.ARTIST_NAME.replace('+', '%20')
            find_id = self._get("search", {'q': self.ARTIST_NAME})
            cter = 0
            for hit in find_id["response"]["hits"]:
                if hit["result"]["primary_artist"]["name"] == self.ARTIST_NAME:
                    cter += 1
                    self.artist_id = hit["result"]["primary_artist"]["id"]
                    self.LIST = self.get_artist_songs(self.artist_id)
                    break

            info = self.get_song_information(self.LIST)
            self.lista =[]
            for item in info:
                name = item['title']
                album = item['album']
                release = item['release_date']
                add = [name, album, release]
                self.lista.append(add)
            page = self.intro_content(self.lista)
            self.wfile.write(bytes(page, 'utf-8'))
        else:
            self.send_error(404)

    def _get(self, path, params=None, headers=None):

        requrl = '/'.join([API_URL, path])
        token = "Bearer {}".format(CLIENT_ACCESS_TOKEN)
        if headers:
            headers['Authorization'] = token
        else:
            headers = {"Authorization": token}

        response = requests.get(url=requrl, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_artist_songs(self, artist_id):
        current_page = 1
        next_page = True
        songs = []

        while next_page:

            path = "artists/{}/songs/".format(artist_id)
            params = {'page': current_page}
            data = self._get(path=path, params=params)

            page_songs = data['response']['songs']

            if page_songs:
                songs += page_songs
                current_page += 1
            else:
                next_page = False

        songs = [song["id"] for song in songs
                 if song["primary_artist"]["id"] == artist_id]

        return songs

    def get_song_information(self, song_ids):
        song_list = []

        for song_id in song_ids:

            path = "songs/{}".format(song_id)
            data = self._get(path=path)["response"]["song"]

            song_list.append(
            {
            "title": data["title"],
            "album": data["album"]["name"] if data["album"] else "<single>",
            "release_date": data["release_date"] if data["release_date"] else "unidentified",
            "featured_artists":
                [feat["name"] if data["featured_artists"] else "" for feat in data["featured_artists"]],
            "producer_artists":
                [feat["name"] if data["producer_artists"] else "" for feat in data["producer_artists"]],
            "writer_artists":
                [feat["name"] if data["writer_artists"] else "" for feat in data["writer_artists"]],
            "genius_track_id": song_id,
            "genius_album_id": data["album"]["id"] if data["album"] else "none"})

            print("-> id:" + str(song_id) + " is finished. \n")
        return song_list

    def intro_content(self, LIST):
        content = ''
        for item in LIST:
            content += '<li>{}</li>'.format(item)
        HTML = '''<html><head><title></title></head>
           <body><ul>
           {}
           </ul></body>
           </html>'''.format(content)
        return HTML




socketserver.TCPServer.allow_reuse_address = True

Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(('', PORT), Handler)
print('serving at port', PORT)
httpd.serve_forever()





