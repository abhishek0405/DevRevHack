import lancedb
import pyarrow as pa
from lancedb.pydantic import LanceModel, Vector

uri = "data/sample-lancedb"
db = lancedb.connect(uri)
schema = pa.schema(
  [
      pa.field("vector", pa.list_(pa.float32(), 3072)),
      pa.field("review", pa.string()),
      pa.field("id",pa.string())
  ])
tbl = db.create_table("reviews_table", schema=schema)

print(tbl)