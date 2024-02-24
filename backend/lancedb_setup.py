import lancedb
import pyarrow as pa

uri = "data/sample-lancedb"
db = lancedb.connect(uri)
schema = pa.schema(
  [
      pa.field("vector", pa.list_(pa.float32(), 1536)),
      pa.field("review", pa.string()),
      pa.field("id",pa.string())
  ])
tbl = db.create_table("review_table", schema=schema)

print(tbl)