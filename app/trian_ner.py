import spacy
from spacy.training.example import Example
import random

# pusty model (tworzymy własny)
nlp = spacy.blank("pl")

ner = nlp.add_pipe("ner")
ner.add_label("FOOD")
ner.add_label("QUANTITY")

TRAIN_DATA = [
    ("kurczak 200g", {"entities": [(0, 7, "FOOD"), (8, 12, "QUANTITY")]}),
    ("frytki 100g", {"entities": [(0, 6, "FOOD"), (7, 11, "QUANTITY")]}),
    ("jajecznica 200g", {"entities": [(0, 10, "FOOD"), (11, 15, "QUANTITY")]}),
    ("spaghetti 300g", {"entities": [(0, 9, "FOOD"), (10, 14, "QUANTITY")]}),
    ("ryz 150g", {"entities": [(0, 3, "FOOD"), (4, 8, "QUANTITY")]}),
]

optimizer = nlp.begin_training()

for i in range(50):
    random.shuffle(TRAIN_DATA)
    losses = {}

    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], losses=losses)

    print(f"Iter {i} Losses {losses}")

# zapis modelu
nlp.to_disk("model")