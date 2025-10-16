import pandas as pd

# Sample stock data
data = {
    'product_name': [
        'Laptop Dell Inspiron',
        'HP Desktop Computer',
        'Wireless Mouse Logitech',
        'Mechanical Keyboard',
        'USB Cable Type-C',
        'A4 Size Paper Ream',
        'Black Gel Pen',
        'Blue Ballpoint Pen',
        'Spiral Notebook A4',
        'Highlighter Marker Set',
        'Office Desk Wooden',
        'Executive Chair',
        'Filing Cabinet 4-Drawer',
        'Conference Table',
        'Bookshelf 5-Tier',
        'LED Monitor 24 inch',
        'HDMI Cable 2m',
        'Laptop Bag',
        'Power Strip 6 Socket',
        'Whiteboard Marker Black',
        'Stapler Heavy Duty',
        'Paper Clips Box',
        'Sticky Notes Pack',
        'Calculator Scientific',
        'Printer HP LaserJet',
        'Printer Ink Cartridge Black',
        'Printer Ink Cartridge Color',
        'Scanner Flatbed',
        'External Hard Drive 1TB',
        'USB Flash Drive 32GB'
    ],
    'quantity': [
        15, 10, 50, 30, 100, 200, 500, 500, 300, 80,
        25, 20, 12, 5, 18, 40, 75, 35, 60, 150,
        45, 200, 120, 25, 8, 40, 40, 6, 20, 100
    ],
    'rate': [
        45000.00, 38000.50, 850.00, 2500.00, 150.00,
        250.00, 10.00, 8.00, 45.00, 120.00,
        12000.00, 8500.00, 15000.00, 35000.00, 6500.00,
        18000.00, 350.00, 1200.00, 450.00, 25.00,
        280.00, 35.00, 65.00, 850.00, 28000.00,
        1200.00, 1500.00, 15000.00, 4500.00, 350.00
    ],
    'category': [
        'Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics',
        'Stationery', 'Stationery', 'Stationery', 'Stationery', 'Stationery',
        'Furniture', 'Furniture', 'Furniture', 'Furniture', 'Furniture',
        'Electronics', 'Electronics', 'Accessories', 'Electronics', 'Stationery',
        'Stationery', 'Stationery', 'Stationery', 'Electronics', 'Electronics',
        'Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'
    ],
    'unit': [
        'pcs', 'pcs', 'pcs', 'pcs', 'pcs',
        'ream', 'pcs', 'pcs', 'pcs', 'set',
        'pcs', 'pcs', 'pcs', 'pcs', 'pcs',
        'pcs', 'pcs', 'pcs', 'pcs', 'pcs',
        'pcs', 'box', 'pack', 'pcs', 'pcs',
        'pcs', 'pcs', 'pcs', 'pcs', 'pcs'
    ],
    'low_stock_alert': [
        5, 3, 10, 8, 20, 50, 100, 100, 50, 15,
        5, 3, 2, 1, 3, 8, 15, 10, 12, 30,
        10, 40, 25, 5, 2, 10, 10, 2, 5, 20
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('sample_stock_import.xlsx', index=False, sheet_name='Stock Import')

print("Excel file created successfully: sample_stock_import.xlsx")
print(f"Total products: {len(df)}")
print(f"Categories: {', '.join(df['category'].unique())}")
print(f"Total quantity: {df['quantity'].sum()}")
print(f"Total value: Rs.{(df['quantity'] * df['rate']).sum():,.2f}")
