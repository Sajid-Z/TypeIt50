import sqlite3

# 150 common English words — short, frequent, no punctuation.
# Good mix of lengths keeps WPM realistic rather than artificially inflated.

WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what", "so",
    "up", "out", "if", "about", "who", "get", "which", "go", "me", "when",
    "make", "can", "like", "time", "no", "just", "him", "know", "take", "people",
    "into", "year", "your", "good", "some", "could", "them", "see", "other", "than",
    "then", "now", "look", "only", "come", "its", "over", "think", "also", "back",
    "after", "use", "two", "how", "our", "work", "first", "well", "way", "even",
    "new", "want", "because", "any", "these", "give", "day", "most", "us", "is",
    "water", "long", "find", "here", "thing", "great", "man", "world", "life", "still",
    "hand", "part", "child", "eye", "woman", "place", "week", "case", "point", "government",
    "company", "number", "group", "problem", "fact", "right", "system", "program", "question", "during",
    "word", "small", "large", "next", "early", "young", "important", "few", "public", "same",
    "able", "high", "every", "between", "own", "old", "different", "follow", "around", "another",
]

def main():
    conn = sqlite3.connect("typeIT50.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM words")
    existing_count = cursor.fetchone()[0]
    if existing_count > 0:
        print(f"words table already populated with {existing_count} rows. Exiting.")
        conn.close()
        return

    cursor.executemany("INSERT INTO words (word) VALUES (?)", [(w,) for w in WORDS])
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()