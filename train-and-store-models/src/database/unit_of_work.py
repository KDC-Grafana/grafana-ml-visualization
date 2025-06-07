class UnitOfWork:
    def __init__(self, connection):
        self.connection = connection
        self.connection.autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()