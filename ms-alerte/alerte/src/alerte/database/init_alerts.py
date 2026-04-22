from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ms_alertes"]

# Création collection avec validation
db.command({
    "create": "alerts",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["_id", "zone_id", "date_heure", "types", "severite"],
            "properties": {
                "_id": {"bsonType": "string"},
                "zone_id": {"bsonType": "string"},
                "date_heure": {"bsonType": "date"},
                "types": {
                    "bsonType": "array",
                    "items": {
                        "enum": [
                            "congestion_detectee",
                            "anomalie_trafic",
                            "fluide_anormal",
                            "capteur_probleme"
                        ]
                    }
                },
                "severite": {
                    "enum": ["low", "medium", "high", "critical"]
                },
                "status": {"bsonType": "string"}
            }
        }
    }
})

# Index
db.alerts.create_index("date_heure")
db.alerts.create_index("zone_id")
db.alerts.create_index("status")

print("DB initialisée")