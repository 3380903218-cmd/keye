import { createDiscussionHandler } from '../_shared/discussion-handler.mjs';

// All credentials stay in the server environment. The website has only an HTTPS URL.
Deno.serve(createDiscussionHandler({ env: Deno.env.toObject() }));
