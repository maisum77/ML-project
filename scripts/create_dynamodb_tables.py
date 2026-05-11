import boto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


def create_table(name, pk, gsis=None):
    existing = [t.name for t in dynamodb.tables.all()]
    if name in existing:
        print(f"  Table '{name}' already exists, skipping")
        return

    key_schema = [{"AttributeName": pk[0], "KeyType": "HASH"}]
    attr_defs = [{"AttributeName": pk[0], "AttributeType": pk[1]}]

    if len(pk) > 2:
        key_schema.append({"AttributeName": pk[2], "KeyType": "RANGE"})
        attr_defs.append({"AttributeName": pk[2], "AttributeType": pk[3]})

    extra = {}
    if gsis:
        gsi_list = []
        for gsi in gsis:
            gsi_key_schema = []
            gsi_attr_defs = []
            for gk in gsi["keys"]:
                gsi_key_schema.append({"AttributeName": gk[0], "KeyType": gk[1]})
                gsi_attr_defs.append({"AttributeName": gk[0], "AttributeType": gk[2]})
            gsi_list.append({
                "IndexName": gsi["name"],
                "KeySchema": gsi_key_schema,
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            })
            for gad in gsi_attr_defs:
                if gad not in attr_defs:
                    attr_defs.append(gad)

        extra["GlobalSecondaryIndexes"] = gsi_list

    provisioned = {
        "ReadCapacityUnits": 5,
        "WriteCapacityUnits": 5,
    }

    if gsis:
        extra["ProvisionedThroughput"] = provisioned
        for gsi in extra.get("GlobalSecondaryIndexes", []):
            gsi.pop("ProvisionedThroughput", None)
            gsi["ProvisionedThroughput"] = provisioned

    params = {
        "TableName": name,
        "KeySchema": key_schema,
        "AttributeDefinitions": attr_defs,
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": provisioned,
    }
    params.update(extra)

    try:
        dynamodb.create_table(**params)
        print(f"  Created table: {name}")
    except Exception as e:
        print(f"  Error creating {name}: {e}")


if __name__ == "__main__":
    print("Creating DynamoDB tables...\n")

    create_table("socialpulse_raw_posts", ("id", "S"), [
        {"name": "platform-index", "keys": [("platform", "HASH", "S"), ("created_at", "RANGE", "S")]},
        {"name": "processed-index", "keys": [("processed", "HASH", "S"), ("created_at", "RANGE", "S")]},
    ])

    create_table("socialpulse_cleaned_posts", ("id", "S"), [
        {"name": "platform-index", "keys": [("platform", "HASH", "S"), ("id", "RANGE", "S")]},
    ])

    create_table("socialpulse_trends", ("topic_id", "S"), [
        {"name": "platform-index", "keys": [("platform", "HASH", "S")]},
    ])

    create_table("socialpulse_sentiment", ("id", "S"), [
        {"name": "label-index", "keys": [("label", "HASH", "S"), ("timestamp", "RANGE", "S")]},
    ])

    create_table("socialpulse_fact_checks", ("id", "S"))

    print("\nTables created successfully.")
    print("Run the backend to start seeding demo data on first launch.")
