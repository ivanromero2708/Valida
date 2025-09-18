#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.models.index_agent import IndexAgentResponse
import json

def test_schema():
    try:
        schema = IndexAgentResponse.model_json_schema()
        print("Schema generated successfully:")
        print(json.dumps(schema, indent=2))
        
        # Check if required field is properly set
        if 'required' in schema:
            print(f"\nRequired fields: {schema['required']}")
            print(f"Properties: {list(schema['properties'].keys())}")
            
            # Verify all properties are in required
            missing_required = set(schema['properties'].keys()) - set(schema['required'])
            extra_required = set(schema['required']) - set(schema['properties'].keys())
            
            if missing_required:
                print(f"WARNING: Properties not in required: {missing_required}")
            if extra_required:
                print(f"ERROR: Required fields not in properties: {extra_required}")
            
            if not missing_required and not extra_required:
                print("✅ Schema validation passed!")
        else:
            print("❌ No 'required' field in schema")
            
    except Exception as e:
        print(f"❌ Error generating schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schema()
