"""
Create a user directly in the database, with a properly hashed password.

Why this exists instead of a POST /register endpoint:
Phase 4 is scoped to the LOGIN side of auth — proving hashing, JWTs, and
a protected endpoint work end-to-end. Public self-registration brings in
its own concerns (email verification, rate limiting signup abuse, etc.)
that belong in a later phase. A seed/admin script is a common real
pattern for exactly this gap — many production systems provision the
first users this way before self-service signup exists.

Usage (from the project root, with your venv active):

    python -m scripts.create_user --email alice@acme.example --password mypassword123 --name Alice --org "Acme Co"

If the organization doesn't exist yet, it's created. If it does, the
user is added to it.
"""

import argparse

from app.core.security import hash_password
from app.db.models import Organization, User
from app.db.session import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a user for local testing/development.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--org", required=True, help="Organization name (created if new)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.name == args.org).first()
        if org is None:
            org = Organization(name=args.org)
            db.add(org)
            db.flush()
            print(f"Created organization '{args.org}' (id={org.id})")

        existing = db.query(User).filter(User.email == args.email).first()
        if existing is not None:
            print(f"A user with email {args.email} already exists (id={existing.id}). Aborting.")
            return

        user = User(
            email=args.email,
            name=args.name,
            organization_id=org.id,
            password_hash=hash_password(args.password),
        )
        db.add(user)
        db.commit()
        print(f"Created user '{args.email}' (id={user.id}) in org '{args.org}'")
    finally:
        db.close()


if __name__ == "__main__":
    main()
