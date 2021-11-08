mail-results
============

A little tool for sending graded PDF files from
programming assignments submitted through Moodle
back to the students.


Installation
------------

Clone the repository, copy `config.sample.ini` to
`config.ini` and adjust the settings there.

Here is an example configuration:
```ini
[email]
address = your.email.here@gmail.com
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_user = your.email.here@gmail.com
```

(For gmail, you might actually have to create an
[app password](https://support.google.com/accounts/answer/185833) for this to work.)



Input Directory
---------------

The input directory has to contain submission directories
in the format `<name>_<number>_...`.

```
submission_dir
	First Student_12345_assignsubmission_file_
		results.pdf
	Second Student_12346_assignsubmission_file
		results.pdf
```


Email Addresses
---------------

You need to create a file `email.csv` with names and
email addresses of the students.
The names have to be exactly like in the
directory names!

```csv
First Student,first.student@example.com
Second Student,second.student@example.com
```

Text
----

You need to prepare the text you want to send to the
students in a plain text file.

You can use the variable `${student}` to insert the
(full) student name.


Running
-------

```
./main.py --email-file email.csv --subject Subject --text-file text.txt directory
```

Check the displayed information and start sending the
messages by entering your SMTP password.
