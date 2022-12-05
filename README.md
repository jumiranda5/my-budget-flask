# MY BUDGET
#### Video Demo:  https://youtu.be/9aJmXcONmFA
#### Description:

My Budget is an application to keep track of personal finances. It was built with Flask and it uses sqlite3 to store the data. This is the final project for the Harvardx course CS50X. It is a Flask version of the command-line application I've build as the final project for the Harvardx course CS50P.

There are three containers in the home page: one for the month, one for the year and one for pending transactions. The month and the year have buttons to get data for the next and previous month/year. Those buttons clicks and the checkboxes for the pending transactions are handled with Javascript, jquery and Ajax. 

On the month page, the data is not updated with Ajax. The next and previous buttons are links instead. The month and year are taken from the route parameters. However, the table row checkbox for payed transactions are handled with Ajax. The delete button is in a form with the 'post' method.

To add a transaction, the user chooses a date, the transaction type (income or expense), the amount, the description, if it repeats and if it is already payed or received.

In the edit page, the user can edit the transaction date (if it has parcels, it will edit the first parcel and move the other parcels to the months following). It is also possible to edit the transaction type, the amount, the description and the parcels count. 