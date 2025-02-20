from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://admin:password@localhost:27017")
db = client["cloudsnippet"]
collection = db["tools"]

async def migrate_tools():
    tools = await collection.find({}).to_list(None)

    for tool in tools:
        updated_troubleshooting = []

        # Handle troubleshooting section
        if "troubleshooting" in tool:
            for item in tool["troubleshooting"]:
                updated_item = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "severity": item.get("severity", "info"),
                    "symptoms": item.get("symptoms", []),
                    "root_cause": item.get(
                        "root_cause", {"description": "", "factors": []}
                    ),
                    "solution": {
                        "steps": [item["solution"]] if isinstance(item.get("solution"), str) else [],
                        "prevention_tips": []
                    },
                }
                updated_troubleshooting.append(updated_item)

        # Prepare update fields
        update_data = {}
        if updated_troubleshooting:
            update_data["troubleshooting"] = updated_troubleshooting

        if update_data:
            await collection.update_one({"_id": tool["_id"]}, {"$set": update_data})

    print(f"Migration complete for {len(tools)} tools.")

import asyncio
asyncio.run(migrate_tools())