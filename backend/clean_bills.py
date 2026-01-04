import sqlite3

# Connect to database
conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()

# Show current bills
print("=" * 60)
print("CURRENT BILLS IN DATABASE")
print("=" * 60)
cursor.execute("""
    SELECT 
        b.id,
        u.username,
        b.bill_type,
        b.bill_date,
        b.units_consumed,
        b.total_amount
    FROM bills b
    JOIN users u ON b.user_id = u.id
    ORDER BY b.id
""")

bills = cursor.fetchall()
for bill_id, username, bill_type, bill_date, units, amount in bills:
    print(f"ID: {bill_id} | User: {username} | Type: {bill_type} | Date: {bill_date} | Units: {units} | Amount: ₹{amount}")

print(f"\nTotal bills: {len(bills)}")
print("=" * 60)

# Ask for confirmation to delete
print("\n⚠️  OPTIONS:")
print("1. Delete ALL bills (clean slate)")
print("2. Delete bills with 0 units/amount (failed OCR)")
print("3. Exit without changes")

choice = input("\nEnter choice (1/2/3): ")

if choice == '1':
    cursor.execute("DELETE FROM bills")
    conn.commit()
    print(f"✅ Deleted ALL {len(bills)} bills. Database is clean!")
elif choice == '2':
    cursor.execute("DELETE FROM bills WHERE units_consumed = 0 OR total_amount = 0")
    deleted = cursor.rowcount
    conn.commit()
    print(f"✅ Deleted {deleted} bills with invalid data")
else:
    print("❌ No changes made")

conn.close()
