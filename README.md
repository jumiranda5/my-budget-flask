# MY BUDGET
#### Video Demo: (CS50x Final Project - My Budget)[https://youtu.be/9aJmXcONmFA]
#### Description:
My Budget is an application that helps users to organize their personal finances. The user can store their income and expenses so they can keep track of their budget. They will see on the home page the month balance, the year balance and the transactions (in/out) that are pending until the current date.

It was built with Flask and uses sqlite3 to store the data. This is the final project for the Harvardx course CS50X. It is a Flask version of the command-line application I've build as the final project for the Harvardx course CS50P.

There are three containers in the home page: one for the month, one for the year and one for pending transactions. The month and the year containers have buttons to get data for the next and previous month/year. Those buttons clicks and the checkboxes for the pending transactions are handled with Javascript, jquery and Ajax, so the data is updated on the page without refreshing.

The month Ajax call will return the balance for the next or previous month along with the total expenses and the total income. Whereas the Ajax call for the year will return the balance for the next or previous year, along with the balance of each month of that same year.

However, the pending container only uses Ajax to update the database, when the "payed" checkbox is clicked. The pending balance and the table with the pending transactions will only be updated on page reload. I've chosen tha approach for simplicity. In addition to that, if there are no pending transactions, the container will be hidden using if/else in the jinja template.

On the month page, the data is not updated with Ajax, for simplicity. The next and previous buttons are links instead. The month and year are taken from the route parameters. However, the table row checkbox for payed transactions are handled with Ajax. The delete button is in a form with the 'post' method and will refresh the page.

To add a transaction, the user chooses a date, the transaction type (income or expense), the amount, the description, if it repeats and if it is already payed or received. If it repeats, the chosen number of transactions will be created for the following months with their parcel number. When the user edits a parcel of a repeated transaction, all the parcels will also be edited, through the parcel_id they share.

In the edit page, the user can edit the transaction date (if it has parcels, it will edit the first parcel and move the other parcels to the months following). It is also possible to edit the transaction type, the amount, the description and the parcels count.

This project uses the python datetime library to get the current date and the calendar library, to get the months names. The next and previous months are handled with functions in the helpers file. If the month is January or December, the next/prev year should change.

For styling, I decided not to use Bootstrap because I wanted to practice CSS.