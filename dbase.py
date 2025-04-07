def notuserexist(cursor, conn, message):
    cursor.execute('SELECT COUNT(*) FROM users')
    number = cursor.fetchone()[0] + 1
    cursor.execute("INSERT INTO users (id, username, ban, number) VALUES (?, ?, ?, ?)",
                   (message.chat.id, message.from_user.username, "FALSE", number))
    conn.commit()

def ban(cursor, message, conn):
    cursor.execute("UPDATE users SET ban = ? WHERE id = ?", ("TRUE", message.from_user.id))
    conn.commit()