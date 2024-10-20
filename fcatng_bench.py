import fcatng
from fcatng import Concept, Context, ConceptLattice
import caspailleur as csp


def caspailleur_test():
    df = csp.io.from_fca_repo('famous_animals_en')
    #print(df.replace({True: 'X', False: ''}))

    concepts_df = csp.mine_concepts(df)

    implications = csp.mine_implications()

    print(concepts_df[['extent', 'intent']].map(', '.join))


def concept_test():
    extent = ['Earth', 'Mars', 'Mercury', 'Venus']
    intent = ['Small size', 'Near to the sun']
    c = Concept(extent, intent)
    print(c)


def concept_lattice_test():
    ct = [
        [True, False, False, False, True, True],
        [True, False, False, True, False, True],
        [False, True, False, False, True, True],
        [False, True, False, True, False, True],
        [False, True, True, False, False, False]
    ]

    attrs = ["cartoon", "real", "tortoise", "dog", "cat", "mammal"]
    objs = ["Garfield", "Snoopy", "Socks", "Greyfriar's Bobby", "Harriet"]

    c = Context(ct, objs, attrs)
    cl = ConceptLattice(c)
    print(cl)


def get_intents():
    ct = [
        [True, False, False, False, True, True],
        [True, False, False, True, False, True],
        [False, True, False, False, True, True],
        [False, True, False, True, False, True],
        [False, True, True, False, False, False]
    ]

    attrs = ["cartoon", "real", "tortoise", "dog", "cat", "mammal"]
    objs = ["Garfield", "Snoopy", "Socks", "Greyfriar's Bobby", "Harriet"]

    c = Context(ct, objs, attrs)

    intents = []

    intents.append(c.get_object_intent("Garfield"))
    intents.append(c.get_object_intent("Snoopy"))
    intents.append(c.get_object_intent("Socks"))
    intents.append(c.get_object_intent("Greyfriar's Bobby"))
    intents.append(c.get_object_intent("Harriet"))

    print(intents)


def get_premises():
    ct = [
        [True, False, False, False, True, True],
        [True, False, False, True, False, True],
        [False, True, False, False, True, True],
        [False, True, False, True, False, True],
        [False, True, True, False, False, False]
    ]

    attrs = ["cartoon", "real", "tortoise", "dog", "cat", "mammal"]
    objs = ["Garfield", "Snoopy", "Socks", "Greyfriar's Bobby", "Harriet"]

    cxt = Context(ct, objs, attrs)
    implication = cxt.get_attribute_implications()

    for imp in implication:
        print(imp)


#get_intents()
#concept_lattice_test()
#caspailleur_test()
get_premises()

premises = [{"cat"}, {"dog"}, {"dog, cat, mammal"}, {"tortoise"},
            {"tortoise, real, mammal"}, {"cartoon"}, {"mammal, real, cartoon"}]
