# Python Programming

The shared repository for the ITMO course. Course rules, lecture materials, and instructions for submitting assignments are published here. The assignments and your solutions live in your own private repository.

## How it works

1. Fill out the registration form and receive an invitation to the private repository `itmo-python-programming/student-<your GitHub username>`.
2. The instructor publishes assignments directly to that repository. Each assignment has its own folder, for example `01_Basic/01_Hello_World/`. It contains a `README.md` with the prompt, a solution file, and public tests in `test_public.py`.
3. Submit your solution by pushing to the `main` branch. GitHub Actions runs the tests after each push; results appear in the repository's Actions tab and are sent to Telegram.
4. Solutions with passing tests are sent for peer review: you review someone else's solution, and others review yours. Reviews are anonymous and take place on the course website; the bot sends you links.

## Getting started

### 1. Accept the invitation

The invitation email will arrive at the address associated with your account. You can also find it at https://github.com/itmo-python-programming. Accept it or you will not be able to access the repository.

### 2. Connect Telegram

Open the link provided by the instructor, in the form `t.me/<bot>?start=CODE`, and press Start. The bot sends new assignments, deadlines, test results, and review assignments.

Bot commands: `/tasks` — your assignments and their statuses; `/reviews` — reviews to complete; `/login` — sign-in link for the website; `/me` — your profile.

### 3. Clone the repository

```bash
git clone git@github.com:itmo-python-programming/student-<username>.git
cd student-<username>
```

If you use HTTPS, you will need a personal access token instead of a password. Setting up an SSH key once is easier: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### 4. Set up your environment

Python 3.13 or later is required.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pytest pytest-timeout
```

## Solving an assignment

Open the assignment's `README.md` and implement the function in the specified file. Change only files inside the assignment folder. Do not edit `test_public.py`; it will be replaced during grading.

Run the tests locally:

```bash
python -m pytest 01_Basic/01_Hello_World
```

When all tests pass, commit and push your solution:

```bash
git add 01_Basic/01_Hello_World
git commit -m "Solve 01_Basic/01_Hello_World"
git push
```

The result will appear in the Actions tab in about a minute. If you see a red cross, open the job named after the assignment to view the pytest log. You can push as many times as you like; the last commit before the deadline is the one that counts.

### When the instructor adds assignments

New assignments appear in the repository in a commit named `Publish …`. Get the latest changes before you start:

```bash
git pull --rebase
```

If you edited only files inside your own assignment folders, there should be no conflicts.

## Peer review

After the deadline (or as soon as your tests pass, depending on the assignment), you will be assigned two other solutions to the same assignment. The bot will send a link; the deadline is usually three days.

On the review page:

- the file list is on the left, code with line numbers is in the center, and the assignment prompt is on the right;
- click `+` next to a line number to comment on that line;
- use the Discussion section for a general comment;
- choose a verdict at the end: Approve or Request changes. Optionally add a summary, then click Finish review.

The author will see your comments only after you finish the review. The author will not see your name, and you will not see the author's name. You can reply to comments on your own solution on the same page.

When reviewing code, look for correctness on edge cases, readability and naming, unnecessary complexity, and compliance with the prompt. Write feedback the way you would like to receive it.

## Course website

Sign in using the link sent by the bot with the `/login` command. The dashboard shows all your assignments, test statuses, reviews received, and reviews you need to complete.

## Rules

- Your solution must be your own. You may discuss ideas, but copying code is not allowed.
- AI tools are permitted, though for homework I recommend completing the work without them: using a ready-made solution does not build the skill.
- Deadlines are shown in the dashboard and in bot messages. Late submissions are marked separately.
