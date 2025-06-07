from src.da.repositories.association_rule_repository import AssociationRuleRepository
from src.da.repositories.decision_tree_repository import DecisionTreeRepository
from src.da.repositories.index_repository import IndexRepository


class ManagerRepository:
    def __init__(self):
        self.tree = DecisionTreeRepository()
        self.index = IndexRepository()
        self.rules = AssociationRuleRepository()

    def get_decision_tree_repository(self):
        return self.tree

    def get_index_repository(self):
        return self.index

    def get_association_rule_repository(self):
        return self.rules
        