from app.platform.sql.tables.documents import DocumentRow   # importing it registers its table

def upgrade(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine, tables=[DocumentRow.__table__])   # SQLModel builds the table from the table model
