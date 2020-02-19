# Till-System
This is a simple point of sale(POS) system which can accomplish the process of ordering and automatically calculate some offers.

Offers:
1. The Meal Deal: A free packet of crisps, popcorn or piece of fruit when a sandwich/panini and a drink are purchased.
2. Hot Drink and a Cookie: A cookie or shortbread half price when a hot drink is purchased.

To run:
1. Executing py till.py from the command prompt while in the directory containing the support files.
OR
2. Run till.py in PyCharm and choose one of the browers given.

Instruction Manual:
1. There are two pages showing all the products -- 'Drinks and Snacks' and 'Sandwiches'. You can switch between them pressing buttons in the bottom left corner.
2. Choose a number you want to purchase and press 'NUM' if it has, the default number is one if you press the name directly.
3. Choose the size of the drink -- Large, Medium and Small and press drink's name if it has and soft drinks are of the same size.
4. You can also order by the plu code of products, enter the plu code and press 'PLU' instead of press its name directly.
5. If order ends, enter the cash value received and press 'CASH' and you'll see the change in title bar. For others payments, just press 'DEBIT' or 'CREDIT'. 
6. You can check the shopping list in the receipt box.
7. If you want to interrupt the order, press 'VOID' and start again.

Database tables(implemented by MySql):
- Products
- Shift
- Payment_method
- Transactions
- Deals
- Pays
