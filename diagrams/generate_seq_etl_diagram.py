from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).with_name("seq_etl_mvc_regenerated.png")
W, H = 1800, 1040

BLUE = "#0f4f73"
TITLE = "#173e72"
CYAN = "#8fd3f4"
BLACK = "#111827"
PALE = "#eff8ff"
WHITE = "#ffffff"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    paths = [
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in paths:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


F_TITLE = font("timesbd.ttf", 34)
F_HEAD = font("arialbd.ttf", 18)
F_SUB = font("arialbd.ttf", 16)
F_LABEL = font("arialbd.ttf", 16)
F_SMALL = font("arialbd.ttf", 14)
F_TINY = font("arial.ttf", 13)


img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)


def text(x, y, value, fnt=F_SMALL, fill=BLACK, anchor=None):
    d.text((x, y), value, font=fnt, fill=fill, anchor=anchor)


def line(points, fill=BLACK, width=2):
    d.line(points, fill=fill, width=width)


def dashed_line(x1, y1, x2, y2, fill=BLACK, width=2, dash=10, gap=7):
    if x1 == x2:
        y = y1
        step = dash + gap
        direction = 1 if y2 >= y1 else -1
        while (direction == 1 and y < y2) or (direction == -1 and y > y2):
            y_end = y + direction * dash
            if direction == 1:
                y_end = min(y_end, y2)
            else:
                y_end = max(y_end, y2)
            d.line((x1, y, x2, y_end), fill=fill, width=width)
            y += direction * step
    else:
        x = x1
        step = dash + gap
        direction = 1 if x2 >= x1 else -1
        while (direction == 1 and x < x2) or (direction == -1 and x > x2):
            x_end = x + direction * dash
            if direction == 1:
                x_end = min(x_end, x2)
            else:
                x_end = max(x_end, x2)
            d.line((x, y1, x_end, y2), fill=fill, width=width)
            x += direction * step


def arrow(x1, y1, x2, y2, fill=BLACK, width=3, dashed=False):
    if dashed:
        dashed_line(x1, y1, x2, y2, fill=fill, width=width)
    else:
        d.line((x1, y1, x2, y2), fill=fill, width=width)
    size = 13
    if x2 >= x1:
        pts = [(x2, y2), (x2 - size, y2 - 7), (x2 - size, y2 + 7)]
    else:
        pts = [(x2, y2), (x2 + size, y2 - 7), (x2 + size, y2 + 7)]
    d.polygon(pts, fill=fill)


def activation(x, y, h):
    d.rectangle((x - 8, y, x + 8, y + h), fill=CYAN, outline=BLUE, width=2)


def self_call(x, y, label1, label2=None):
    d.line((x + 8, y, x + 62, y, x + 62, y + 30, x + 8, y + 30), fill=BLACK, width=2)
    d.polygon([(x + 8, y + 30), (x + 20, y + 23), (x + 20, y + 37)], fill=BLACK)
    text(x + 78, y - 2, label1, F_SMALL)
    if label2:
        text(x + 78, y + 21, label2, F_SMALL)


def view_self_call(y, label1, label2=None):
    x = 570
    d.line((x - 8, y, x - 64, y, x - 64, y + 30, x - 8, y + 30), fill=BLACK, width=2)
    d.polygon([(x - 8, y + 30), (x - 20, y + 23), (x - 20, y + 37)], fill=BLACK)
    text(230, y + 1, label1, F_SMALL)
    if label2:
        text(230, y + 24, label2, F_SMALL)


def actor(x, y):
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=CYAN, outline=BLUE, width=2)
    line((x, y + 10, x, y + 46), width=2)
    line((x - 25, y + 23, x + 25, y + 23), width=2)
    line((x, y + 46, x - 25, y + 80), width=2)
    line((x, y + 46, x + 25, y + 80), width=2)


def participant_view(x, y):
    line((x - 76, y - 34, x - 76, y + 36), width=2)
    line((x - 76, y, x - 30, y), width=2)
    d.ellipse((x - 28, y - 23, x + 18, y + 23), fill=CYAN, outline=BLUE, width=2)


def participant_round(x, y, title, subtitle):
    d.ellipse((x - 23, y - 23, x + 23, y + 23), fill=CYAN, outline=BLUE, width=2)
    line((x - 34, y + 23, x + 34, y + 23), width=2)
    text(x, 146, title, F_HEAD, anchor="mm")
    text(x, 174, subtitle, F_SUB, anchor="mm")


# Border and title
d.rounded_rectangle((6, 6, W - 6, H - 6), radius=8, fill=WHITE, outline=TITLE, width=3)
text(30, 25, "Diagramme de séquence MVC - Lancement du pipeline ETL", F_TITLE, TITLE)

# Participants
admin_x, view_x, ctrl_x, model_x = 145, 570, 1035, 1505
actor(admin_x, 82)
text(admin_x, 178, "Administrateur", F_HEAD, anchor="mm")

participant_view(view_x, 105)
text(view_x, 150, "View", F_HEAD, anchor="mm")
text(view_x, 178, "(Interface Admin)", F_SUB, anchor="mm")

participant_round(ctrl_x, 105, "Controller", "(FastAPI Controller)")
participant_round(model_x, 105, "Model / Service", "(ETL Runner + DB)")

# Lifelines and activations
for x in (admin_x, view_x, ctrl_x, model_x):
    dashed_line(x, 195, x, 995, width=2, dash=6, gap=6)
activation(admin_x, 210, 735)
activation(view_x, 225, 720)
activation(ctrl_x, 335, 542)
activation(model_x, 455, 290)

# Flow
arrow(admin_x + 8, 235, view_x - 12, 235)
text(245, 214, "1 : Accéder au module ETL", F_LABEL)

arrow(admin_x + 8, 304, view_x - 12, 304)
text(250, 283, '2 : Cliquer sur "Run ETL pipeline"', F_LABEL)

arrow(view_x + 10, 354, ctrl_x - 12, 354)
text(640, 324, "3 : POST /admin/import/run-etl", F_LABEL)
text(675, 348, "(mode, demo_users, truncate, dry_run)", F_SMALL)

self_call(ctrl_x, 386, "3.1 : Vérifier JWT", "et rôle admin")
self_call(ctrl_x, 448, "3.2 : Valider les paramètres")
self_call(ctrl_x, 510, "3.3 : Créer ImportLog", "(status = running)")

arrow(ctrl_x + 10, 585, model_x - 12, 585)
text(1165, 560, "4 : Démarrer la tâche ETL en arrière-plan", F_LABEL)

self_call(model_x, 615, "4.1 : Extraire depuis prod_db")
self_call(model_x, 672, "4.2 : Transformer et normaliser")
self_call(model_x, 729, "4.3 : Charger dans", "analytics_db")
self_call(model_x, 786, "4.4 : Enregistrer logs", "et métriques")

arrow(ctrl_x - 8, 633, view_x + 12, 633, dashed=True)
text(700, 603, "5 : Réponse immédiate", F_LABEL)
text(673, 627, '{log_id, status: "running"}', F_SMALL)

# Polling loop box
d.rounded_rectangle((520, 670, 1120, 862), radius=8, fill=PALE, outline=TITLE, width=2)
d.rounded_rectangle((538, 655, 750, 683), radius=5, fill=WHITE, outline=TITLE, width=2)
text(552, 661, "loop toutes les 2 secondes", F_SMALL, TITLE)

arrow(view_x + 10, 704, ctrl_x - 12, 704, fill=BLUE)
text(642, 684, "6 : GET /run-etl/{log_id}/status", F_SMALL)
arrow(ctrl_x - 8, 742, view_x + 12, 742, dashed=True)
text(666, 722, "7 : status, progression, étape courante", F_SMALL)
arrow(view_x + 10, 783, ctrl_x - 12, 783, fill=BLUE)
text(642, 763, "8 : GET /run-etl/{log_id}/log", F_SMALL)
arrow(ctrl_x - 8, 821, view_x + 12, 821, dashed=True)
text(692, 801, "9 : lignes de log récentes", F_SMALL)

view_self_call(884, "10.1 : Afficher la progression", "et les logs en temps réel")
view_self_call(935, "10.2 : Afficher le résultat final")

arrow(view_x - 12, 982, admin_x + 12, 982, dashed=True)
text(240, 963, "11 : Consulter le résultat d'exécution", F_LABEL)

# Data note
d.rounded_rectangle((1292, 250, 1682, 390), radius=8, fill="#f7fbff", outline=BLUE, width=2)
d.ellipse((1322, 270, 1418, 298), fill="#f7fbff", outline=BLUE, width=2)
d.rectangle((1322, 284, 1418, 334), fill="#f7fbff", outline=BLUE, width=2)
d.ellipse((1322, 320, 1418, 348), fill="#f7fbff", outline=BLUE, width=2)
text(1445, 278, "Données ETL", F_HEAD)
text(1445, 308, "Source : prod_db", F_SMALL)
text(1445, 334, "Cible : analytics_db", F_SMALL)
text(1445, 360, "Audit : import_logs", F_SMALL)

text(30, 1004, "Version régénérée : flux asynchrone FastAPI, suivi par polling status/log et historique ImportLog.", F_TINY, "#475569")

img.save(OUT, quality=95)
print(OUT)
