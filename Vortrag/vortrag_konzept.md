## Vortrag

### Idee/Ziel

 * wir bauene einen MusicRecommender auf der Basis von Linked Data
 * Input: eine Band
 * Output: Vorschläge für weitere Bands auf Basis von Relationen, die nicht unbedingt offensichtlich sind
 * Idee dabei: related Bands, die nicht bei Spotify etc. sind
 * Ziel im high level: "Zum erforschen und entdecken von Bands"
 * Buzzwords: Dashboard, Recommendation, 
 * "nicht statisch, immer weiter entdecken durch weiterklicken"
 * -> Analogie zu Wikipedia
 * Relationen: Membership Relation, Producer Relation...
 * Votingsystem erklären
 * warum ist das cool?: 
 * Adressat: Musikinteressenten, Interesse an den Bands selbst (wer spielt mit etc.)
 * -> haben selbst schon Bands entdeckt
 * Mehrwert: Direkt Musik anbieten, durchklicken, schnelles dynamisches Entdecken, Begründungen

### Demo

 * Screencast machen, Features zeigen

### Datenquellen

 * Schaubild schön machen und erklären (was woher, warum)
 * dbtune ist musicbrainz mapping
 * musicbrainz id ist sehr praktisch bei anderen APIs
 * dbtune owl:sameAs -> dbpedia
 * dbpedia: Zentrum des linked open webs
 * EchoNest: per musicbrainz id
 * Events über Songkick
 * Mucke über Spotify (und Bier aus der Flasche)
 * Problem, die dabei Auftreten (Überleitung)

### Probleme/Lösungen

 * Probleme:
 * 1.) Datenquellen unvollständig (bzw. nicht alle Bands auffindbar)
 * Stichwort DBPedia
 * Lösung: Discogs? tradeoff: beschränkte Funktionalität, aber Mehrwertgenerierung für DBPedia -> parsen
 * 2.) Musicbrainz liegt nicht komplett als RDF vor (Musicbrainz ist die DIE Datenquelle für Musik, dbtune nicht vollständig -> Einschränkung)(?)
 * Lösung: Discogs? tradeoff: beschränkte Funktionalität, aber Mehrwertgenerierung für DBPedia -> parsen 
 * 3.) dbtune Endpoint nicht sehr schnell und nicht aktuell, Sparql 1.0
 * Lösung: ???
 * 4.) Input mapping
 * Lösung: educated Guess (Titlecase) und string indexing
 * 5.) keine Fallbacks
 * Lösung: anstatt zu dbtune, mbid ausm Dump und dbpedia von dbpedia

### Ausblick

 * Parser: alles was nicht rdf ist, als rdf parsen. 
 * -> and DBPedia schicken um DBPedia zu erweitern
 * Parser funktioniert schon teilweise, aber noch nicht vollständig
 * mehr aus Events rausholen
 * JSON hat Koordinaten -> Anbindung an linked geo data??? noch zu klären
 * URI statt bzw. zusätzlich zum Namen