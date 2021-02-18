import re
import random

class Sentence:

    tag_parser = re.compile(R"<(?P<contents>(?:name|nom|obj|poss|posspro|refl)|(?:verb: (?P<verb>[^>]+)))>")
    cap_parser = re.compile(R"([?!.][ \t\"\']{1,})")

    irregular_verbs = {
        "be" : [
            "is",
            "are"
        ],
        "do" : [
            "does",
            "do"
        ],
        "have" : [
            "has",
            "have"
        ]
    }


    def __init__(self, template_string): 
        self.raw = template_string
        self.processed = template_string
        self.tags = {"replaced":[], "types":[], "verbs": [], "sets":[], "raw": []}
    def find_tags(self):
        tag_iter = Sentence.tag_parser.finditer(self.raw)
        for tag in tag_iter: # get a sequence of the tag types in order
            self.tags["types"].append("verb" if tag.groupdict().get("verb",None) else tag.groupdict().get("contents"))
            self.tags["raw"].append(f"<{tag.groupdict().get('contents',None)}>")
            self.tags["verbs"].append(tag.groupdict().get("verb",None))

    def process_tags(self, pronoun_sets, names): # pronoun_sets should be a list of Row objects or dict-likes
        for i, tag in enumerate(self.tags["types"]):
            if tag == "name":
                self.tags["replaced"].append(random.choice(names))
                self.tags["sets"].append(None)
            elif tag == "verb":
                lastNomIndex = i - self.tags["types"][i::-1].index("nom")
                plural = self.tags["sets"][lastNomIndex]["plural"]
                if self.tags["verbs"][i] in Sentence.irregular_verbs:
                    self.tags["replaced"].append(Sentence.irregular_verbs[self.tags["verbs"][i]][plural])
                else:
                    self.tags["replaced"].append(self.tags["verbs"][i] + ("s" if not plural else ""))
                
                self.tags["sets"].append(None)
            else:
                current_set = random.choice(pronoun_sets)

                self.tags["replaced"].append(current_set[tag])

                self.tags["sets"].append(current_set)

    def replace_tags(self):
        for i,rawtag in enumerate(self.tags["raw"]):
            self.processed = self.processed.replace(rawtag, self.tags["replaced"][i], 1)
        self.processed = "".join([sentence[0].upper() + sentence[1:] for sentence in Sentence.cap_parser.split(self.processed)])

    def process_all(self, pronoun_sets, names):
        self.find_tags()
        self.process_tags(pronoun_sets, names)
        self.replace_tags()

        return self.processed
        


if __name__ == "__main__":
    testSentence = Sentence("<name> is really cool! <nom> <verb: be> fun and funky and we love <obj> very much! Another sentence. Yet another.")

    print(testSentence.process_all([{"nom":"they","obj":"them","plural":1},{"nom":"she","obj":"her","plural":0}], ["name1", "name2"]))
    
        
         