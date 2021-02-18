from euphy.util.db import SentenceDBCursor

with open("sentences.txt") as sfile:
    sentences = [[sentence[:-1]] for sentence in sfile.readlines()]

with SentenceDBCursor() as sentencedb:
    print(sentences[0])
    print(sentencedb.add_sentences(sentences))