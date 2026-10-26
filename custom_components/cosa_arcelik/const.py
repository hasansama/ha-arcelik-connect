DOMAIN = "cosa_arcelik"
API_ROOT = "https://kiwi.cosa.com.tr/api"
PROVIDER = "arcelik"
POLL_SECONDS = 30

# Arçelik Connect APK: dikey gösterim 1–6, API 6–1.
VERTICAL = {
    "Tam aşağı": 6,
    "Aşağı": 5,
    "Hafif aşağı": 4,
    "Hafif karşıya": 3,
    "Karşıya yakın": 2,
    "Tam karşıya": 1,
    "Otomatik salınım": 100,
}
# Yatay ara açıların fiziksel yönleri henüz doğrulanmadı.
HORIZONTAL = {
    "Tam sola": 13,
    "Ara konum 1": 1,
    "Ara konum 2": 2,
    "Ara konum 3": 3,
    "Ara konum 4": 4,
    "Ara konum 5": 5,
    "Tam sağa": 35,
    "Otomatik salınım": 100,
}
FAN_SPEED = {"1": 2, "2": 3, "3": 4, "4": 5, "5": 6}
MODE_TO_CODE = {"cool": 0, "dry": 1, "fan_only": 2, "heat": 4}
CODE_TO_MODE = {v: k for k, v in MODE_TO_CODE.items()}
