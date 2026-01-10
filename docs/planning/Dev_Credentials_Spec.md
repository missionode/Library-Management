# Development Credentials & Secrets Specification

## 1. Purpose
This document (and the corresponding `dev_secrets.json` to be created) serves as a centralized repository for all development-time credentials, keys, and secrets. It ensures that the development team has easy access to test accounts and configuration keys without hardcoding them into the main codebase logic.

**WARNING:** This file is for **DEVELOPMENT AND TESTING ONLY**. Do not use these credentials in a live production environment.

## 2. File Structure (Target: `dev_secrets.json`)
We will generate a JSON file during Phase 1 containing the following structure:

```json
{
  "django_secret_key": "will-be-generated-automatically",
  "superusers": [
    {
      "username": "admin",
      "email": "admin@library.local",
      "password": "AdminPassword123!",
      "role": "ADMIN"
    }
  ],
  "librarians": [
    {
      "username": "lib_jane",
      "email": "jane@library.local",
      "password": "LibrarianPassword123!",
      "role": "LIBRARIAN"
    }
  ],
  "members": [
    {
      "username": "member_john",
      "email": "john@library.local",
      "password": "MemberPassword123!",
      "role": "MEMBER"
    }
  ],
  "api_keys": {
    "openai_api_key": "sk-placeholder",
    "gemini_api_key": "placeholder"
  }
}
```

## 3. Usage Strategy
1.  **Creation:** An initialization script (`scripts/init_dev_data.py`) will be written in Phase 1 to read this file and populate the database automatically.
2.  **Updates:** If new test users or keys are needed, update the source file and re-run the init script.
3.  **Security:** This file helps isolate secrets so they can be easily added to `.gitignore` later if the repo goes public, while still keeping a template for other developers.
