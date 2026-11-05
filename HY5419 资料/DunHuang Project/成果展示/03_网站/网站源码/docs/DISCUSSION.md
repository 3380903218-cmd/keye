# Public reader discussion

Release 2.9.1, prepared on 3 November 2026. The Supabase database and public function are deployed and have passed real save/read/reply, retry and moderation checks. GitHub Pages publication is recorded in the release verification file.

The discussion follows the sources chapter. Readers supply a display name, select an optional topic and post a question or suggestion. Replies stay under the original question. Reading and posting require no visitor account. Messages and replies may be written in any language. English and Chinese switch only the interface, preserving the reader's original text and unfinished draft. There is no voting, pop-up or notification subscription.

## Data boundary

Activation is controlled by `enabled` in `dist/discussion-config.js`. When it is `false`, the section and footer link remain hidden and make no discussion requests. The published release is enabled after cloud acceptance. Browser storage holds only a random identifier used for a basic posting limit; **messages are never stored in local storage**. Offline exports link to the online discussion when the service is enabled.

The GitHub Pages site remains static. `supabase/functions/dunhuang-discussion/index.ts` runs the public HTTPS handler. It accesses two server-only PostgreSQL RPC functions using the server environment's secret key. The public website contains only the function URL. No database key, administrator password or access token belongs in `dist/` or Git.

The tables live in `discussion_private`. Row-level security is enabled and browser roles cannot read the tables or execute the RPC functions. All functions use invoker privileges. Only the server service role receives the required schema, table and function grants; the Supabase service role bypasses RLS by design. The public API returns visible display names, message bodies, categories, server timestamps and thread/reply pagination, without internal rate hashes. SQL parameters, text rendering, request-size limits and retry identifiers protect the write/read boundary. An ambiguous network failure preserves the draft rather than claiming success or definite failure.

Display names are self-chosen and do not authenticate a person or identify the project owner. Reader comments remain separate from verified historical evidence. The first release does not let a pseudonymous visitor edit or delete a saved message; moderation remains with the project owner.

## Deployment and maintenance

1. Confirm a project on the Free plan, preferably in Singapore. Do not upgrade billing or change an unrelated existing project. If no suitable free project can be created, ask the owner before a paid action.
2. Apply `supabase/migrations/20261102162018_create_reader_discussion.sql` once as a migration.
3. Deploy the function and its shared module with JWT verification **disabled** for this deliberately public endpoint. Keep privileged database calls on the server; do not grant browser roles RPC access.
4. Supabase injects `SUPABASE_URL` and server secret keys. The handler accepts the current `SUPABASE_SECRET_KEYS` dictionary, a `SUPABASE_SECRET_KEY`, or a legacy service-role key as a fallback. For a new deployment prefer current secret keys. The optional `DISCUSSION_RATE_SECRET` can separate rate hashing from the database credential.
5. `DISCUSSION_ALLOWED_ORIGINS` defaults to `https://3380903218-cmd.github.io`. Add another exact origin only when the exhibition is deliberately published there. Do not use `*` or a production localhost allowance.
6. Test the real endpoint from the GitHub Pages origin: independent readers post/read/reply, refresh persists data, a repeated request does not duplicate a row, and hiding the specific test thread removes it from the public list. Remove only identified test records through the owner's database access.
7. Activate with `python3 tools/configure_discussion.py --enable https://PROJECT_REF.supabase.co/functions/v1/dunhuang-discussion`. This performs a real read and CORS check before changing the browser configuration. It does not substitute for write/reply or mainland-network verification.
8. Update the release version, verify static hashes, publish through the existing GitHub Pages workflow, and check the live website. Refresh both offline exports from the same source. Do not claim a new mainland access test without an actual visitor result.

## Owner moderation and export

In the Supabase dashboard, select the `discussion_private` schema and open `messages`. A root has `parent_id = NULL`; each reply's `parent_id` is the root's `id`.

- Set `hidden = true` on an unwanted message. Hiding a root also excludes its replies from public API responses. Set it back to `false` to restore visibility.
- Delete a root only when deletion is intended: its replies are removed by the foreign-key cascade. Hiding is the reversible default.
- Export this table to CSV from the owner dashboard for review. Do not put unreviewed raw exports in the public website repository.
- Disable the website module with `python3 tools/configure_discussion.py --disable` and publish that change if the discussion needs to be paused. Saved messages remain in the database.

The handler limits a visitor to eight posts per ten minutes, with a five-second gap, and uses a looser network bucket to avoid treating a classroom Wi-Fi as one reader. It stores daily salted hashes, not plaintext IP addresses, in a non-public table. Old buckets are cleaned on subsequent writes. These are basic abuse controls, not verified identity or a guarantee against deliberate distributed spam. The hosting provider may keep separate infrastructure logs.

## Verification

The tests run the actual migration on PGlite's PostgreSQL engine and call the production HTTP handler. They cover shared threads, replies, idempotency after a lost response, moderation, pagination, rate limits, restricted database roles and persistence after reopening the database. Browser acceptance uses two independent storage contexts, the complete exhibition HTML, desktop/mobile layouts and literal untrusted text.

```sh
cd tests/discussion
npm ci
npm test
```

For `browser.mjs`, also install `playwright-core` in a QA environment and provide `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE` if needed. `PGLITE_MODULE` and `DISCUSSION_QA_OUTPUT` can select an external test installation and artifact directory. Disposable test data never seeds the public service.

Local checks are supplemented by deployed API and browser checks for this release. They do not establish access from mainland China; a new visitor test is required for the discussion service. The Free plan may pause a project after inactivity; check and resume it before a presentation if necessary. The route map and Gephi network initialise independently of the discussion.

References checked on 2 November 2026: [Supabase secrets](https://supabase.com/docs/guides/functions/secrets), [function CORS](https://supabase.com/docs/guides/functions/cors), [database function privileges](https://supabase.com/docs/guides/database/functions), [API keys](https://supabase.com/docs/guides/getting-started/api-keys), [Free plan](https://supabase.com/pricing).

## Current service

Project: `dunhuang-discussion` (`qtuxpxccweapkqeoaata`), Singapore (`ap-southeast-1`), in the owner-approved personal organization. The quoted project cost at creation was **USD 0/month** on the Free plan. [Owner dashboard](https://supabase.com/dashboard/project/qtuxpxccweapkqeoaata/editor).

The security advisor reported only the expected informational notice that the two private, server-only tables have RLS enabled with no browser policies. This intentionally defaults to denial; no browser roles receive schema/table/RPC access. [Explanation of the informational notice](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy). New indexes can appear as unused before the database has traffic; they support thread pagination and reply lookups. [Index usage notice](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index).
