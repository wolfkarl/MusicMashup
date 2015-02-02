import codecs

file = codecs.open('dumps/queens_of_the_stone_age.ttl', 'r', 'utf-8')
print ("LADE DATEN! ======================================================")
count = -1
for line in file:
	count += 1
	if 'prefix' in line:
		True
	elif 'abstract' in line: 
		# self.abstract = line.split(' ', 2)[2][1:-4]
		print line.split(' ', 2)[2][1:-4]
	elif 'currentMember' in line and line.split(' ', 2)[0] == ":"+"Queens of the Stone Age".replace(' ', '_'):
		temp = line.split(' ', 2)[2][1:-3]
		# self.currentMembers.append("http://dbpedia.org/ressource/"+temp)
		print temp
	elif 'formerMember' in line and line.split(' ', 2)[0] == ":"+"Queens of the Stone Age".replace(' ', '_'):
		temp = line.split(' ', 2)[2][1:-3]
		# self.currentMembers.append("http://dbpedia.org/ressource/"+temp)
		print temp
	elif 'dbtune' in line:
		# self.dbtuneURL = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'musicbrainz.org' in line:
		# self.musicbrainzID = line.split(' ',2)[2][31:-4]
		print (line.split(' ',2)[2][31:-4])	
	elif 'commons.dbpedia' in line and "owl:sameAs" in line:
		# self.dbpediaCommonsURL = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'myspace' in line:
		# self.myspace = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])	
	elif 'twitter' in line:
		# self.twitter = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'musixmatch' in line:
		# self.musixmatch_url = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'wikipedia' in line:
		# self.wikipedia = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'mm:official' in line:
		# self.official = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])	
	elif 'last.fm' in line:
		# self.lastfm = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'discogs' in line:
		# self.discogs_url = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'dbpedia-owl:thumbnail' in line:
		# self.thumbnail = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'foaf:image' in line:
		# self.images.append(line.split(' ',2)[2][1:-4])
		print (line.split(' ',2)[2][1:-4])
	elif 'mm:musicbrainzID' in line:
		# self.musicbrainzID = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'mm:spotifyID' in line:
		# self.spotifyID = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'mm:echonestArtist' in line:
		# self.echoNestArtist = line.split(' ',2)[2][1:-4]
		print (line.split(' ',2)[2][1:-4])
	elif 'mm:recommendedArtist' in line:
		artist = "http://dbpedia.org/resource/"+line.split(' ', 2)[2][1:-3]
		voteValue = float(file.next().split(' ', 2)[2][:-3])
		familiarity = float(file.next().split(' ', 2)[2][:-3])
		print artist
		print voteValue
		print familiarity
		# artistObject = MusicMashupArtist(artist, voteValue, "", False)
		# artistObject.familiarity = familiarity
		tempLine = file.next()
		# count += 3
		while 'mm:recommendedArtist' not in tempLine:
			if 'currentMember' in tempLine:
				reason = "Because " + tempLine.split(' ', 2)[0][1:] + " is a member of this band."
				# artistObject.reason.append(reason)
				print reason
			elif 'formerMember' in tempLine:
				reason = "Because " + tempLine.split(' ', 2)[0][1:] + " was a member of this band."
				# artistObject.reason.append(reason)
				print reason
			elif 'producer' in tempLine:
				reason = "Because " + tempLine.split(' ', 2)[0][1:] + " was active as producer."
				# artistObject.reason.append(reason)
				print reason
			elif 'writer' in tempLine:
				reason = "Because " + tempLine.split(' ', 2)[0][1:] + " was active as writer."
				# artistObject.reason.append(reason)
				print reason
			tempLine = file.next()
			count += 1
		# self.recommendation.append(artistObject)
		# file.seek(count+1)