import argparse
import csv
import configparser
import smtplib
import mimetypes
import getpass
from email.message import EmailMessage
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass
from glob import glob
from string import Template


@dataclass
class Submission:
    directory: Path
    files: List[Path]
    student: str
    address: str


def send_email(
    sender: str,
    recipient: str,
    subject: str,
    text: str,
    smtp_server: str,
    smtp_password: str,
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    attachments: Optional[List[Path]] = None,
) -> None:
    if smtp_user is None:
        smtp_user = sender

    print(f'Sending message to {recipient}')

    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message.set_content(text)

    for attachment_file in attachments:
        ctype, encoding = mimetypes.guess_type(str(attachment_file))
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'

        print(f'\tAttaching {attachment_file.name} ({ctype})')

        maintype, subtype = ctype.split('/', 1)
        with open(attachment_file, 'rb') as f:
            message.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=attachment_file.name,
            )

    session = smtplib.SMTP(smtp_server, smtp_port)
    session.starttls()
    session.login(smtp_user, smtp_password)
    session.sendmail(sender, recipient, message.as_string())
    session.quit()

    print('ok')


def read_email_addresses(path: Path) -> Dict[str, str]:
    with open(path) as f:
        reader = csv.reader(f)
        return {
            row[0].strip(): row[1].strip()
            for row in reader
            if len(row) >= 2
        }


def find_submissions(
    directory: Path,
    email_addresses: Dict[str, str],
    filter: str
) -> List[Submission]:
    submissions = []
    for submission_dir in directory.iterdir():
        # format: <name>_<whatever>
        if not submission_dir.is_dir():
            continue

        if '_' not in submission_dir.name:
            print(f'Warning: Directory name contains no "_", skipping: {submission_dir}')
            continue

        name = submission_dir.name.split('_')[0]

        if name not in email_addresses:
            print(f'Error: No email address found for "{name}"')
            continue

        files = [
            Path(x)
            for x in glob(str(submission_dir / filter))
        ]
        if len(files) == 0:
            print(f'Error: No files found for "{name}" ("{filter}")')
            continue

        submissions.append(Submission(
            directory=submission_dir,
            files=files,
            student=name,
            address=email_addresses[name],
        ))

    return submissions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--email-file', type=Path)
    parser.add_argument('--filter', default='*.pdf')
    parser.add_argument('--subject', required=True)
    parser.add_argument('--text-file', required=True)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()

    directory = args.directory

    # read configuration and email mapping
    config = configparser.ConfigParser()
    config.read(Path(__file__).parent / 'config.ini')

    email_addresses = read_email_addresses(args.email_file)
    print(f'Found {len(email_addresses)} email addresses')

    # find and display submissions
    submissions = find_submissions(directory, email_addresses, args.filter)

    print('Submissions:')
    for submission in submissions:
        print(
            f'{submission.directory.name}\n\t=> {submission.student} <{submission.address}> ({submission.files})'
        )
    print()

    # text
    with open(args.text_file) as f:
        text = ''.join(f.readlines())

    print(f'Subject: {args.subject}')
    print(f'Text:\n{text}')
    print()

    text = Template(text)

    # password
    print('Note: for gmail you may need to create an app password!')
    smtp_password = getpass.getpass(prompt='SMTP server password: ')

    # send
    for submission in submissions:
        send_email(
            recipient=submission.address,
            subject=args.subject,
            text=text.substitute({
                'student': submission.student
            }),
            attachments=submission.files,
            sender=config['email']['address'],
            smtp_server=config['email']['smtp_server'],
            smtp_port=int(config['email'].get('smtp_port', 587)),
            smtp_user=config['email'].get('smtp_user', None),
            smtp_password=smtp_password,
        )


if __name__ == '__main__':
    main()
