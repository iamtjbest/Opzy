import { E2E_USER_PATTERN, psql } from "./db";

/**
 * Delete the users this suite created, so the dev database doesn't fill up with them.
 * Everything else they touched goes with them: the schema cascades from users.
 */
export default function teardown() {
  if (psql(`delete from users where email like '${E2E_USER_PATTERN}'`) === null) {
    console.warn("e2e teardown: couldn't delete the test users. Clean them up by hand.");
  }
}
