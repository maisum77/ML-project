import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.app.core.config import get_settings

settings = get_settings()

dynamodb = boto3.resource(
    "dynamodb",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

_raw_posts_table = dynamodb.Table(settings.dynamodb_raw_posts_table)
_cleaned_posts_table = dynamodb.Table(settings.dynamodb_cleaned_posts_table)
_trends_table = dynamodb.Table(settings.dynamodb_trends_table)
_sentiment_table = dynamodb.Table(settings.dynamodb_sentiment_table)
_fact_checks_table = dynamodb.Table(settings.dynamodb_fact_checks_table)
_propagation_table = dynamodb.Table(settings.dynamodb_propagation_table)


def _serialize_value(v):
    from decimal import Decimal
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, float):
        return Decimal(str(v))
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, dict):
        return {k: _serialize_value(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_serialize_value(item) for item in v]
    return v


def _serialize_item(item):
    return {k: _serialize_value(v) for k, v in item.items()} if item else None


def _serialize_items(items):
    return [_serialize_item(item) for item in items]


class DynamoDBCollection:
    def __init__(self, table, name: str):
        self.table = table
        self.name = name

    async def get(self, id: str):
        try:
            response = self.table.get_item(Key={"id": id})
            return _serialize_item(response.get("Item"))
        except Exception as e:
            print(f"[DynamoDB] Error getting item from {self.name}: {e}")
            return None

    async def find_one(self, query=None):
        if isinstance(query, dict):
            if "id" in query:
                return await self.get(query["id"])
            elif "original_id" in query:
                try:
                    response = self.table.get_item(Key={"id": query["original_id"]})
                    return _serialize_item(response.get("Item"))
                except Exception as e:
                    print(f"[DynamoDB] Error in find_one for {self.name}: {e}")
                    return None
            else:
                cursor = await self.find(query)
                items = await cursor.to_list(length=1)
                return items[0] if items else None
        elif isinstance(query, str):
            return await self.get(query)
        else:
            cursor = await self.find({})
            items = await cursor.to_list(length=1)
            return items[0] if items else None

    async def find(self, query: Optional[Dict] = None):
        if query and any(v is not None for v in query.values()):
            platform = query.get("platform")
            if platform:
                return await self._query_by_platform(platform)
            doc_id = query.get("id")
            if doc_id:
                item = await self.get(doc_id)
                return DynamoDBCursor([item] if item else [])
        return await self._scan_all()

    async def _scan_all(self):
        try:
            items = []
            response = self.table.scan()
            items.extend(response.get("Items", []))
            while "LastEvaluatedKey" in response:
                response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                items.extend(response.get("Items", []))
            return DynamoDBCursor(items)
        except Exception as e:
            print(f"[DynamoDB] Error scanning {self.name}: {e}")
            return DynamoDBCursor([])

    async def _query_by_platform(self, platform: str):
        try:
            response = self.table.query(
                IndexName="platform-index",
                KeyConditionExpression=Key("platform").eq(platform),
            )
            return DynamoDBCursor(response.get("Items", []))
        except Exception as e:
            print(f"[DynamoDB] Error querying {self.name} by platform: {e}")
            try:
                items = []
                resp = self.table.scan()
                items.extend(resp.get("Items", []))
                while "LastEvaluatedKey" in resp:
                    resp = self.table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
                    items.extend(resp.get("Items", []))
                filtered = [item for item in items if item.get("platform") == platform]
                return DynamoDBCursor(filtered)
            except Exception:
                return DynamoDBCursor([])

    async def insert_one(self, doc: dict):
        try:
            item = _serialize_item(doc)
            self.table.put_item(Item=item)
            return item
        except Exception as e:
            print(f"[DynamoDB] Error inserting into {self.name}: {e}")
            return doc

    async def update_one(self, query: dict, update: dict, upsert: bool = False):
        try:
            doc_id = query.get("id") or query.get("original_id")
            if not doc_id:
                print(f"[DynamoDB] update_one requires 'id' or 'original_id' in query for {self.name}")
                return None

            set_data = update.get("$set", {})
            if not set_data:
                return None

            update_expression_parts = []
            expression_values = {}
            expression_names = {}
            for i, (k, v) in enumerate(set_data.items()):
                placeholder = f":val{i}"
                name_placeholder = f"#attr{i}"
                update_expression_parts.append(f"{name_placeholder} = {placeholder}")
                expression_values[placeholder] = _serialize_value(v)
                expression_names[name_placeholder] = k

            update_expression = "SET " + ", ".join(update_expression_parts)

            kwargs = {
                "Key": {"id": doc_id},
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": expression_values,
                "ExpressionAttributeNames": expression_names,
                "ReturnValues": "UPDATED_NEW",
            }

            if not upsert:
                kwargs["ConditionExpression"] = "attribute_exists(id)"

            try:
                response = self.table.update_item(**kwargs)
                return response.get("Attributes")
            except self.table.meta.client.exceptions.ConditionalCheckFailedException:
                return None
        except Exception as e:
            print(f"[DynamoDB] Error updating {self.name}: {e}")
            return None

    async def count_documents(self, query: Optional[Dict] = None):
        if query:
            platform = query.get("platform")
            if platform:
                try:
                    response = self.table.query(
                        IndexName="platform-index",
                        KeyConditionExpression=Key("platform").eq(platform),
                        Select="COUNT",
                    )
                    return response.get("Count", 0)
                except Exception:
                    pass
            doc_id = query.get("id")
            if doc_id:
                item = await self.get(doc_id)
                return 1 if item else 0

        try:
            count = 0
            response = self.table.scan(Select="COUNT")
            count += response.get("Count", 0)
            while "LastEvaluatedKey" in response:
                response = self.table.scan(
                    Select="COUNT",
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                count += response.get("Count", 0)
            return count
        except Exception as e:
            print(f"[DynamoDB] Error counting {self.name}: {e}")
            return 0

    def aggregate(self, pipeline: Optional[list] = None):
        return DynamoDBAggregateCursor(self, pipeline)


class DynamoDBAggregateCursor:
    def __init__(self, collection: DynamoDBCollection, pipeline: Optional[list] = None):
        self.collection = collection
        self.pipeline = pipeline or []
        self._filter_unprocessed = False
        self._limit = None
        self._sort_field = None
        self._sort_order = 1
        self._skip = 0

        for stage in self.pipeline:
            if "$match" in stage:
                match = stage["$match"]
                if match.get("processed", {}).get("$ne") in (True, "true") or match.get("processed") in (False, "false"):
                    self._filter_unprocessed = True
            if "$limit" in stage:
                self._limit = stage["$limit"]
            if "$sort" in stage:
                sort_expr = stage["$sort"]
                if sort_expr:
                    field = list(sort_expr.keys())[0]
                    self._sort_field = field
                    self._sort_order = sort_expr[field]

    def sort(self, field, order=1):
        self._sort_field = field
        self._sort_order = order
        return self

    def skip(self, count):
        self._skip = count
        return self

    def limit(self, count):
        self._limit = count
        return self

    async def to_list(self, length=None):
        cursor = await self.collection._scan_all()
        items = list(cursor.data)

        if self._filter_unprocessed:
            items = [item for item in items if not item.get("processed")]

        if self._sort_field:
            reverse = self._sort_order == -1
            items.sort(
                key=lambda x: x.get(self._sort_field, 0) or 0,
                reverse=reverse,
            )

        items = items[self._skip:]
        limit = length or self._limit
        if limit:
            items = items[:limit]

        return items


class DynamoDBCursor:
    def __init__(self, data: list):
        self.data = [_serialize_item(d) for d in data]
        self._sort_field = None
        self._sort_order = 1
        self._skip = 0
        self._limit = None

    def sort(self, field, order=1):
        self._sort_field = field
        self._sort_order = order
        return self

    def skip(self, count):
        self._skip = count
        return self

    def limit(self, count):
        self._limit = count
        return self

    async def to_list(self, length=None):
        result = list(self.data)
        if self._sort_field:
            reverse = self._sort_order == -1
            result.sort(
                key=lambda x: x.get(self._sort_field, 0) or 0,
                reverse=reverse,
            )
        result = result[self._skip:]
        if self._limit:
            result = result[:self._limit]
        if length:
            result = result[:length]
        return result


raw_posts = DynamoDBCollection(_raw_posts_table, "raw_posts")
cleaned_posts = DynamoDBCollection(_cleaned_posts_table, "cleaned_posts")
trends = DynamoDBCollection(_trends_table, "trends")
sentiment = DynamoDBCollection(_sentiment_table, "sentiment")
fact_checks = DynamoDBCollection(_fact_checks_table, "fact_checks")
propagation = DynamoDBCollection(_propagation_table, "propagation")
