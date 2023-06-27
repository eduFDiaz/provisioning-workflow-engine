from typing import List
from cassandra.query import SimpleStatement
from config import logger as log
from Models.Errors.ErrorMetadata import ErrorModel

class ErrorDao:
    def __init__(self, session):
        self.session = session

    def get_all_errors(self) -> List[ErrorModel]:
        stmt = SimpleStatement("SELECT * FROM workflows.Errors", fetch_size=100)
        errors = self.session.execute(stmt)
        return [ErrorModel(**error._asdict()) for error in errors]

    def get_errors_by_correlationID(self, requestID) -> List[ErrorModel]:
        """ This method returns all errors for a given requestID."""
        stmt = SimpleStatement("""
            SELECT * 
            FROM workflows.Errors 
            WHERE "correlationID"=%s
        """, fetch_size=100)
        errors = self.session.execute(stmt, [requestID])
        #sort errors by timeStamps
        errors = sorted(errors, key=lambda error: error.timeStamp)
        return [ErrorModel(**error._asdict()) for error in errors]
    
    def delete_errors_by_correlationID(self, requestID):
        """ This method deletes all errors for a given requestID."""
        stmt = SimpleStatement("""
            DELETE 
            FROM workflows.Errors 
            WHERE "correlationID"=%s
        """, fetch_size=100)
        self.session.execute(stmt, [requestID])

    def add_or_update_error(self, error: ErrorModel):
        """ By design, Cassandra performs Upserts. so this stamement will also update
            the record if a record whith such composite key already exists.
        """
        stmt = SimpleStatement("""
            INSERT INTO workflows.Errors (
                "correlationID", "timeStamp", "error"
                ) VALUES (%s, %s, %s)
        """)
        self.session.execute(stmt, [
            error.correlationID,
            error.timeStamp,
            error.error
        ])