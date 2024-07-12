class RelationWithProperties:
    def __init__(self, relation, properties, rel_type = ""):
        self.relation = relation
        self.properties = properties
        self.rel_type = rel_type
    
    def get_properties(self):
        return self.properties

    def get_rel_type(self):
        return self.rel_type

    def get_relation(self):
        return self.relation

    def to_tuple(self):
        tuple_rel = tuple(self.relation )
        if not self.properties:
           return (tuple_rel)
        else:
            tuple_properties = tuple(self.properties)
            return (tuple_rel, tuple_properties)
    
    def __str__(self) -> str:
        return str(self.to_tuple()) 
    
    '''
    def __repr__(self) -> str:
        return str(self.to_tuple())  
    '''

class VbDobjRelationWithProperties(RelationWithProperties):
    #vb =relation[1]
    #dobj = relation[2]
    def __init__(self, relation, properties):
        self.rel_type = relation[0]
        self.relation = relation
        self.properties = properties
        self.verb = relation[1]
        self.dobj = relation[2]

    def get_verb(self):
        return self.verb
    
    def get_dobj(self):
        return self.dobj

class VbIndObjRelationWithProperties(RelationWithProperties):
      
    def __init__(self, relation, preposition, properties):
        self.rel_type = relation[0]
        self.relation = relation
        self.verb = relation[1]
        self.indobj = relation[2]
        self.properties = properties
        self.preposition = preposition

    def get_preposition(self):
        return self.preposition
    
    def get_verb(self):
        return self.verb
    
    def get_indobj(self):
        return self.indobj

    def to_tuple(self):
        tuple_rel = tuple(self.relation )
        if self.properties:
           tuple_properties = tuple(self.properties)
           return (tuple_rel, self.preposition, tuple_properties)
        else:
           return (tuple_rel, self.preposition)

class VbNoobjRelation(RelationWithProperties):
    # as of 05.22 no relationships supported
    def __init__(self, relation):
        self.rel_type = relation[0]
        self.relation = relation
        self.verb = relation[1]

    def to_tuple(self):
        tuple_rel = tuple(self.relation )
        return (tuple_rel)

    def get_verb(self):
        return self.verb

class VbDobjIndobjRelationWithProperties(RelationWithProperties):
      
    def __init__(self, relation, preposition, properties):
        self.rel_type = relation[0]
        self.verb = relation[1]
        self.dobj = relation[2]
        self.indobj = relation[3]
        self.preposition = preposition
        self.properties = properties
        self.relation = relation

    def get_verb(self):
        return self.verb
    
    def get_dobj(self):
        return self.dobj

    def get_indobj(self):
        return self.indobj
    
    def get_preposition(self):
        return self.preposition

    def to_tuple(self):
        tuple_rel = tuple(self.relation )
        if self.properties:
           tuple_properties = tuple(self.properties)
           return ((tuple_rel, self.preposition, tuple_properties))
        else:
           return (tuple_rel, self.preposition)
            
if __name__ == "__main__":

    example_rel_part = ['dobj', 'open', 'cupboard']
    example_preposition_part = "for"
    example_properties = [('property', 'cupboard', 'big'), ('property', 'cupboard', 'wooden')]

    example_prop_2 = [('property', 'cupboard', 'small')]
    a = VbDobjRelationWithProperties(example_rel_part, example_properties)
    print("s")