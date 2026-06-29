"""Allow `python3 -m job_hunt auth|plan|push`."""

from job_hunt.resume_sync_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
