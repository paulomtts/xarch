# importing it registers its table
from app.platform.sql.tables.documents import DocumentRow

def upgrade(engine: Engine) -> None:
    # SQLModel builds the table from the table model
    SQLModel.metadata.create_all(engine, tables=[DocumentRow.__table__])
