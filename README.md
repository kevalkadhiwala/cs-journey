# Keval Kadhiwala

[![tests](https://github.com/kevalkadhiwala/cs-journey/actions/workflows/tests.yml/badge.svg)](https://github.com/kevalkadhiwala/cs-journey/actions/workflows/tests.yml)

I'm a Computer Science student at Dublin City University. I mostly like
backend work and security. This repo has the two projects I've spent
the most time on.

## Projects

### Cybersecurity Log Analyzer
Python · FastAPI · SQLite · Pydantic · LLMs · JavaScript · pytest · Docker

Reads authentication logs and picks out brute force, password spraying,
logins that succeed after a run of failures, and accounts attacked from
many IPs at once. Every suspicious IP gets a risk score, and you can look
through it all in a REST API and a dashboard.

There's an optional AI incident report on top. The model only explains
what my rules found, its answers are validated, and it has defences
against prompt injection hidden in usernames. I also built a labelled
evaluation set to score it. With the AI off, you get a rule-based report
instead. 77 tests, and it runs in Docker.

[Go to the project →](./Projects/cybersecurity-log-analyzer)

### Student Grade Manager
Python · OOP · SQLite · FastAPI · LLM tool calling · pytest · Docker

Started as an OOP exercise and grew into a proper app. It has SQLite
storage, a command line, marks per subject and term, and a REST API.
The optional AI assistant answers questions like "who's below 40 in
Databases?" by calling four read-only functions I wrote. It never writes
SQL, and every number in its answer is checked against real results.
56 tests, and it runs in Docker.

[Go to the project →](./Projects/student-grade-manager)

## Skills

Python · Java · C/C++ · SQL · SQLite · FastAPI · JavaScript · HTML/CSS ·
pytest · Docker · Git/GitHub

## Education

BSc Computer Science, Dublin City University
