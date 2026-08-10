"""Best-effort emoji per product, picked by keyword match on the item name.

This is a simple keyword dictionary, not real categorization - there's no
category field in the price-transparency feed, only free-text product
names. It'll catch common, common-sense cases (dairy, meat, bread, socks...)
and fall back to a generic cart emoji for anything unrecognized or unusual
brand names. Order matters: more specific keywords are checked first so
e.g. "ביצים" (eggs) doesn't get swallowed by a broader poultry match.
"""

_KEYWORD_EMOJI = [
    (("גרביים", "גרב "), "\U0001f9e6"),  # socks
    (("תחתונים", "תחתוני"), "\U0001fa72"),
    (("ביצים", "ביצה"), "\U0001f95a"),
    # Chocolate/sweets checked before dairy: "שוקולד חלב" (milk chocolate)
    # contains the word "חלב" (milk) and would otherwise be mis-tagged.
    (("שוקולד", "וופל", "עוגיות", "ממתק", "סוכריות"), "\U0001f36b"),
    (("חלב",), "\U0001f95b"),
    (("גבינה", "גבינת", "קוטג"), "\U0001f9c0"),
    (("יוגורט", "אשל", "דנונה"), "\U0001f963"),
    (("חמאה", "מרגרינה"), "\U0001f9c8"),
    (("עוף", "פרגית", "כנפ", "שוקית", "חזה עוף"), "\U0001f357"),
    (("הודו",), "\U0001f983"),
    (("בקר", "עגל", "סטייק", "אנטריקוט", "המבורגר", "קבב", "שישליק"), "\U0001f969"),
    (("דג ", "דגים", "סלמון", "טונה", "פילה"), "\U0001f41f"),
    (("נקניק", "נקניקיה", "סלמי", "פסטרמה"), "\U0001f32d"),
    (("לחם", "חלה", "בגט", "פיתה"), "\U0001f35e"),
    (("עוגה", "עוגי", "מאפה", "קרואסון"), "\U0001f9c1"),
    (("גלידה", "ארטיק"), "\U0001f368"),
    (("במבה", "ביסלי", "חטיף", "צ'יפס", "פופקורן"), "\U0001f37f"),
    (("תפוח", "אגס"), "\U0001f34e"),
    (("בננה",), "\U0001f34c"),
    (("עגבני", "פלפל", "מלפפון", "ירק", "חסה", "בצל", "תפוח אדמה", "גזר"), "\U0001f96c"),
    (("פירות", "אבטיח", "מלון", "ענבים", "תות"), "\U0001f347"),
    (("קפה", "נס קפה", "אספרסו"), "☕"),
    (("תה ",), "\U0001f375"),
    (("מיץ", "נקטר"), "\U0001f9c3"),
    (("קולה", "משקה קל", "סודה", "פחית"), "\U0001f964"),
    (("בירה",), "\U0001f37a"),
    (("יין",), "\U0001f377"),
    (("אורז", "פסטה", "ספגטי", "קוסקוס", "בורגול"), "\U0001f35d"),
    (("שמן", "זית"), "\U0001f6e2"),
    (("קמח", "סוכר", "אבקת אפיה"), "\U0001f9c2"),
    (("שימורים", "טונה בקופסה", "תירס משומר"), "\U0001f96b"),
    (("ניקוי", "אקונומיקה", "סבון כלים", "מרכך", "אבקת כביסה"), "\U0001f9fc"),
    (("נייר טואלט", "מגבונים", "טישו"), "\U0001f9fb"),
    (("שמפו", "מרכך שיער", "סבון", "דאודורנט", "משחת שיניים"), "\U0001f9f4"),
    (("חיתולים", "מגבוני תינוק", "מטרנה", "סימילאק", "תרכובת"), "\U0001f37c"),
    (("מזון לכלב", "מזון לחתול", "חול לחתול"), "\U0001f43e"),
    (("קפוא", "מוקפא"), "\U0001f9ca"),
]

_DEFAULT_EMOJI = "\U0001f6d2"  # shopping cart


def pick_emoji(text):
    if not text:
        return _DEFAULT_EMOJI
    for keywords, emoji in _KEYWORD_EMOJI:
        if any(keyword in text for keyword in keywords):
            return emoji
    return _DEFAULT_EMOJI
