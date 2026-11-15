class DocumentRow(SQLModel, table=True):   # the table model: the database's shape, defined once
    __tablename__ = "documents"
    id: UUID = Field(primary_key=True)
    title: str
    published_at: datetime | None = None
