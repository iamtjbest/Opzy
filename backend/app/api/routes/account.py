from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession, Limiter
from app.core.rate_limit import ACCOUNT_DELETE_PER_IP
from app.core.security import verify_password
from app.schemas.auth import AccountDelete

router = APIRouter(prefix="/account", tags=["account"])


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    body: AccountDelete, user: CurrentUser, db: DbSession, limiter: Limiter
) -> None:
    """Delete the logged-in user and everything that hangs off them.

    A hard delete: the `users` row goes, and the `ON DELETE CASCADE`s declared in
    `docs/schema.sql` take the profile, its skills and interests, every saved/dismissed/
    applied action, the notification log, and both token tables with it. Nothing is kept,
    so the address is immediately free to sign up again as a brand-new account.
    """
    # Throttled before the Argon2 verify below, which costs ~64 MB a call.
    await limiter.enforce("account-delete", ACCOUNT_DELETE_PER_IP)

    # The current password, not just a valid token: a stolen or borrowed session should not
    # be enough to destroy an account irreversibly.
    #
    # 403, not 401. The session is perfectly valid — it's the password that's wrong — and
    # everything in this app treats a 401 as "your token has expired": the frontend's
    # apiFetch turns one into a redirect through /session/end, so answering 401 here would
    # log the user out for the crime of a typo.
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="That password is incorrect.",
        )

    await db.delete(user)
    await db.commit()
