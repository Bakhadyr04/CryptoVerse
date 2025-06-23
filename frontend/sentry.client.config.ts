import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "https://2590e5737648de5a82cf08c8ff91ad34@o4509509550145536.ingest.us.sentry.io/4509509657296896",
  tracesSampleRate: 1.0,
});
