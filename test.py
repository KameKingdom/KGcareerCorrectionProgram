import MeCab
wakati = MeCab.Tagger("-Owakati")
print(wakati.parse("pythonが大好きです").split())