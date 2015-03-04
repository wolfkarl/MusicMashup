# Howto install MusicMashup

 1. Clone GitHub repository
 
 ```
 git clone https://github.com/kaozente/MusicMashup.git 
 ```
    
 2. Install **Python 2.7** and **pip**
 3. Install necessary packages:
 
 ```
 pip install SPARQLWrapper discogs_client titlecase pyechonest datetime cherrypy mako rdfextras
 ```

 4. Start the MusicMashup server. Wait for the parsing to finish
  ```
  python MusicMashupServer.py
  ```

 5. Open `localhost:8080` in your browser. 
