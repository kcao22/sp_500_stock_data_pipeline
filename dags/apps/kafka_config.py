schemas = {
    "transactions": {
        "key_schema": """{
            "type": "record",
            "name": "transaction_partition_key",
            "fields": [
                {"name": "company_id", "type": "int"}
            ]
        }""",
        "value_schema": """{
            "type": "record",
            "name": "transaction_value",
            "fields": [
                {"name": "transaction_id", "type": "string"},
                {"name": "customer_id", "type": "int"},
                {"name": "company_id", "type": "int"},
                {"name": "volume_traded", "type": "int"},
                {"name": "transaction_timestamp_utc", "type": "string"}
            ]
        }"""
    }
}
