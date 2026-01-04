import sqlite3

# Connect to database
conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()

# Show current bills
print("=" * 80)
print("CURRENT BILLS IN DATABASE")
print("=" * 80)
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
    WHERE b.units_consumed > 0 AND b.total_amount > 0
    ORDER BY b.id
""")

bills = cursor.fetchall()
print(f"\n{'ID':<5} {'User':<15} {'Type':<12} {'Date':<12} {'Units':<10} {'Amount':<10}")
print("-" * 80)
for bill_id, username, bill_type, bill_date, units, amount in bills:
    print(f"{bill_id:<5} {username:<15} {bill_type:<12} {bill_date:<12} {units:<10.1f} ₹{amount:<10.2f}")

print(f"\nTotal valid bills: {len(bills)}")
print("=" * 80)

if len(bills) == 0:
    print("No valid bills found. Upload some bills first!")
    conn.close()
    exit()

# Options
print("\n📋 UPDATE OPTIONS:")
print("1. Auto-split: Mark EVEN bill IDs as 'water', ODD as 'electricity'")
print("2. Manual: Choose bill IDs to mark as 'water' (rest stay 'electricity')")  
print("3. Exit without changes")

choice = input("\nEnter choice (1/2/3): ").strip()

if choice == '1':
    # Auto-split
    cursor.execute("UPDATE bills SET bill_type = 'water' WHERE id % 2 = 0")
    cursor.execute("UPDATE bills SET bill_type = 'electricity' WHERE id % 2 = 1")
    conn.commit()
    
    # Show result
    cursor.execute("SELECT COUNT(*) FROM bills WHERE bill_type = 'water'")
    water_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bills WHERE bill_type = 'electricity'")
    elec_count = cursor.fetchone()[0]
    
    print(f"\n✅ Updated successfully!")
    print(f"   - Water bills: {water_count}")
    print(f"   - Electricity bills: {elec_count}")

elif choice == '2':
    # Manual selection
    print("\nEnter bill IDs to mark as WATER (comma-separated, e.g., 1,3,5):")
    water_ids = input("IDs: ").strip()
    
    if water_ids:
        ids = [int(x.strip()) for x in water_ids.split(',') if x.strip().isdigit()]
        
        # First, set all to electricity
        cursor.execute("UPDATE bills SET bill_type = 'electricity'")
        
        # Then set selected ones to water
        for bill_id in ids:
            cursor.execute("UPDATE bills SET bill_type = 'water' WHERE id = ?", (bill_id,))
        
        conn.commit()
        print(f"\n✅ Marked {len(ids)} bills as water!")
    else:
        print("❌ No IDs provided")

else:
    print("❌ No changes made")

conn.close()
