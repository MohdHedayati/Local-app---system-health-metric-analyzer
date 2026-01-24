import json
from genson import SchemaBuilder

builder = SchemaBuilder()

with open('/home/archuserbtw/.ai_device_monitor/data/history.json', 'r') as f:
    obj = json.load(f)
    builder.add_object(obj)

# Print the formal schema
print(builder.to_json(indent=2))