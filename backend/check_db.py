import sqlite3

# Connect to database
conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()

# Check users
cursor.execute("SELECT id, username FROM users")
users = cursor.fetchall()

print("=" * 50)
print("DATABASE SUMMARY")
print("=" * 50)
print(f"\nTotal Users: {len(users)}")
for user_id, username in users:
    cursor.execute("SELECT COUNT(*) FROM bills WHERE user_id = ?", (user_id,))
    bill_count = cursor.fetchone()[0]
    print(f"  - {username} (ID: {user_id}): {bill_count} bills")

# Get bill details
print("\n" + "=" * 50)
print("BILL DETAILS")
print("=" * 50)
cursor.execute("""
    SELECT 
        u.username, 
        b.bill_date, 
        b.units_consumed, 
        b.total_amount 
    FROM bills b 
    JOIN users u ON b.user_id = u.id 
    ORDER BY b.bill_date
""")
bills = cursor.fetchall()

if bills:
    for username, bill_date, units, amount in bills:
        print(f"{username} | {bill_date} | {units} units | ₹{amount}")
else:
    print("No bills found in database!")

print("\n" + "=" * 50)

conn.close()
