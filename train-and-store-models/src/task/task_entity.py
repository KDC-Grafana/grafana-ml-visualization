class TaskCreateModel:
    def __init__(self, id, id_source, algorithm, parameters, state):
        self.id = id
        self.id_source = id_source
        self.algorithm = algorithm
        self.parameters = parameters
        self.state = state

class TaskDeleteModel:
    def __init__(self, id, id_model, state, date):
        self.id = id
        self.id_model = id_model
        self.state = state
        self.date = date

class TaskCreateSource:
    def __init__(self, id, name, description, creator, source, target, state):
        self.id = id
        self.name = name
        self.description = description
        self.creator = creator
        self.source = source
        self.target = target
        self.state = state

class TaskDeleteSource:
    def __init__(self, id, id_source, state, date):
        self.id = id
        self.id_source = id_source
        self.state = state
        self.date = date
