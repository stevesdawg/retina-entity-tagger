import nltk
from wikidata import WikidataEntityLookup
from dbco import *

wd = WikidataEntityLookup()
def lookupNamedEntities(namedEntityTexts):
    '''
    Given list of texts that correspond to named entities,
    return a list of dictionaries, where each dict has 
    the original text, entity id, and description.

    Example usage:
    lookupNamedEntities(['NYC', 'New York State', 'USA'])
    should return [
        {'text': 'NYC', 'id': 'Q60', 'description': 'city in state of New York...'},
        {'text': 'New York State', 'id': 'Q1380', 'description': 'state in us..'}, ..
    ]
    '''
    returned_list = []    
    
    for i in xrange(len(namedEntityTexts)):
        entity = namedEntityTexts[i]
        entity_info = wd.searchEntities(entity)
        if entity_info is not None:
            entity_info['text'] = entity
        else:
            entity_info = {'text': entity, 'id': '-1'} # -1 is no results from wikidata
        returned_list.append(entity_info)
        
    return returned_list

def getNameEntities(text):
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    nameEntity = []
    for sentence in chunked_sentences:
        for part in sentence:
            if type(part) is nltk.Tree:
                entityTree = part.leaves()
                entity = ""
                for tuplePair in entityTree:
                    entity += " "
                    entity += tuplePair[0]
                entity = entity[1:]
                nameEntity.append(entity)
    nameEntity = list(set(nameEntity))
    return lookupNamedEntities(nameEntity)

# def entityTester():
#     with open("small_sample_articles.json") as f:
#         for line in f:
#             print(getNameEntities(json.loads(line)["content"]))

def getArticlesNoEntities(limit=1000):
    articles = db.qdoc.find({ "$query": { "entities": { "$exists": False } }, "$orderby": { '_id' : -1 } }).limit(limit)
    return articles

#Driver
def tagEntities():
    articles = getArticlesNoEntities()
    for a in articles:
        db.qdoc.update( { "_id": a['_id'] },{"$set": {"entities": getNameEntities(a['content'] ) } } )

if __name__ == "__main__":
    tagEntities()
