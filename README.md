**1. Installation**
Download the program files (ensure you have Python installed).

Run main.py to start the application.

**2. How to Add Your Own Cases**
To create and add custom cases, follow this folder structure:

Case Folder Structure
cases/
└── [Case Name]/
    ├── case.png            (Case thumbnail image)
    ├── case.txt            (Case name and price)
    ├── items.txt           (List of items in the case)
    └── sprites/
        ├── [Item]_[Skin].png   (Item images)
        └── ...
Step-by-Step Setup
1. Create a Case Folder
Inside the cases folder, create a new folder with your case name (e.g., Dragon Case).

2. Add case.png
Place a 300x300px image named case.png inside the case folder.

Example:
cases/Dragon Case/case.png

3. Create case.txt
This file defines the case name and price.

Format:
Dragon Case
5.50

First line: Case name
Second line: Price in dollars

4. Create items.txt
This file lists all items inside the case.

Format per line:
[Item];[Skin];[Price];[Rarity]

Example:
AK-47;Redline;125.50;rare
AWP;Dragon Lore;2500.00;legendary
M4A4;Howl;1000.00;mythical

Rarity options: common, uncommon, rare, mythical, legendary

5. Add Item Images (sprites/ folder)
Create a sprites folder inside your case folder.

Add images for each item in the format:
[Item]_[Skin].png

Example:
AK-47_Redline.png
AWP_Dragon Lore.png

Recommended size: 200x200px for best display.

**3. Using the Application**
Main Menu
Open Cases – Browse and open available cases.

Inventory – View and sell your items.

Exit – Close the application.

Opening a Case
Click "Open Cases".

Select a case you can afford.

Watch the animation to see what you unboxed!

The item will be added to your Inventory.

Managing Inventory
Sell Items Individually – Click the "Sell" button next to an item.

Bulk Selling:

Check the boxes of items you want to sell.

Click "Select All" / "Deselect All" if needed.

Click "Sell Selected" to sell multiple items at once.

Money System
You start with $1000.00.

Selling items adds money to your balance.

Opening cases costs money (price varies per case).

**4. Troubleshooting**
Common Issues
❌ "Case not appearing in the list?"
→ Ensure the folder is inside cases/ and has the correct files (case.txt, case.png, items.txt, sprites/).

❌ "Item images not showing?"
→ Check that images are named correctly (e.g., AK-47_Redline.png).

❌ "Error when opening a case?"
→ Verify items.txt formatting (no missing lines or incorrect prices).

❌ "Inventory not saving?"
→ The app creates backups (inventory.txt.bak), so you can restore if needed.